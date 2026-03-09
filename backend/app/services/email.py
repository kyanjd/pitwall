import datetime

import resend
from app.core.config import settings
from app.db.session import get_session_local
from app.models.f1 import F1Session
from app.models.game import Game, GameUser
from app.models.prediction import Prediction
from app.models.user import User
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import col, select


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    def _send(self, to: str, subject: str, html: str) -> resend.Emails.SendResponse:
        params: resend.Emails.SendParams = {
            "from": "Pitwall <onboarding@resend.dev>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        return resend.Emails.send(params)

    def send_prediction_reminder(self, to: str, session_name: str, session_date: str) -> resend.Emails.SendResponse:
        subject = f"Reminder: Submit your predictions for {session_name}!"
        html = f"""
        <p>Make sure to submit your predictions for the upcoming F1 session:</p>
        <ul>
            <li><strong>Session:</strong> {session_name}</li>
            <li><strong>Date:</strong> {session_date}</li>
        </ul>
        <p>Prediction entry locks on race start.</p>
        <p>Make your prediction at <a href="https://pitwall-tau.vercel.app">Pitwall</a>.</p>
        """
        return self._send(to=to, subject=subject, html=html)


mailer = EmailService()

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", minutes=30)
async def send_prediction_reminders():
    now = datetime.datetime.now(datetime.timezone.utc)
    now_plus_1h = now + datetime.timedelta(hours=1)

    with get_session_local() as session:
        statement = select(F1Session).where(
            F1Session.date >= now, F1Session.date < now_plus_1h, F1Session.type == "Race"
        )
        upcoming_session = session.exec(statement).first()
        if not upcoming_session:
            return

        games = session.exec(select(Game)).all()
        for game in games:
            if game.season != upcoming_session.race.season:
                continue

            already_predicted = select(Prediction.user_id).where(
                Prediction.game_id == game.id,
                Prediction.f1session_id == upcoming_session.id,
            )
            unpredicted_users = session.exec(
                select(User)
                .join(GameUser, GameUser.user_id == User.id)
                .where(
                    GameUser.game_id == game.id,
                    col(User.id).not_in(already_predicted),
                )
            ).all()

            for user in unpredicted_users:
                try:
                    response = mailer.send_prediction_reminder(
                        to=user.email,
                        session_name=f"{upcoming_session.race.name}",
                        session_date=upcoming_session.date.strftime("%Y-%m-%d %H:%M UTC"),
                    )
                except Exception as e:
                    print(f"Failed to send email to {user.email}: {e}")
