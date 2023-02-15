from dataclasses import dataclass


@dataclass
class CandidateBase:
    district_id: str
    lg_id: str
    ward_num: int
    party: str
    name: str

    @staticmethod
    def is_name_valid(name):
        return all(
            [
                name.strip(),
                name[0:3] != '...',
                name[0:1] != '-',
                name[0:3] != '___',
                str(name).strip() != '(None)',
            ]
        )

    @property
    def is_valid(self):
        return self.is_name_valid(self.name)

    def to_dict(self):
        return {
            'district_id': self.district_id,
            'lg_id': self.lg_id,
            'ward_num': self.ward_num,
            'party': self.party,
            'name': self.name,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            district_id=d['district_id'],
            lg_id=d['lg_id'],
            ward_num=(int)(d['ward_num']),
            party=d['party'],
            name=d['name'],
        )
