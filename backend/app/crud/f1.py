from sqlmodel import Session, select

from app.models.f1 import Circuit


def upsert_circuit(*, session: Session, circuit: Circuit) -> Circuit:
    statement = select(Circuit).where(Circuit.external_id == circuit.external_id)
    existing_circuit = session.exec(statement).first()

    if existing_circuit:
        existing_circuit.name = circuit.name
        existing_circuit.locality = circuit.locality
        existing_circuit.country = circuit.country
        session.add(existing_circuit)
        return existing_circuit
    else:
        session.add(circuit)
        return circuit
