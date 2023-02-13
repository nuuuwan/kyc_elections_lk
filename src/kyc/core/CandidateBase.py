from dataclasses import dataclass


@dataclass
class CandidateBase:
    district_id: str
    lg_id: str
    ward_name: str
    name: str
