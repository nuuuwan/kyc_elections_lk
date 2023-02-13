from dataclasses import dataclass


@dataclass
class CandidateBase:
    district_id: str
    lg_id: str
    ward_name: str
    party_name: str
    name: str

    def to_dict(self):
        return {
            'district_id': self.district_id,
            'lg_id': self.lg_id,
            'ward_name': self.ward_name,
            'party_name': self.party_name,
            'name': self.name,
        }
