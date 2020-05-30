from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class QualificationType(object):
    Name: str
    Description: str
    Keywords: str = ""
    IsRequestable: bool = True
    AutoGranted: bool = False
    AutoGrantedValue: int = 0
    Test: Optional[str] = None
    AnswerKey: Optional[str] = None
    TestDurationInSeconds: Optional[int] = None
    RetryDelayInSeconds: int = 30
    QualificationTypeStatus: str = "Active"
    QualificationTypeId: Optional[str] = None
    CreationTime: Optional[datetime] = None

    def __post_init__(self):
        assert self.RetryDelayInSeconds >= 30,\
            f"RetryDelayInSeconds should be greater of equal 30, received {self.RetryDelayInSeconds}"
        assert self.QualificationTypeStatus in ["Active", "Inactive"],\
            f"QualificationTypeStatus should be one of 'Active' or 'Inactive', received {self.QualificationTypeStatus}"
        test_validation_errors = self._validate_test(self.Test)
        assert len(test_validation_errors) == 0, "\n".join(test_validation_errors)
        answer_validation_errors = self._validate_answer(self.AnswerKey)
        assert len(answer_validation_errors) == 0, "\n".join(answer_validation_errors)

    def _validate_test(self, test: Optional[str]) -> List[str]:
        if not test:
            return []
        # TODO Implement the test validation
        return []

    def _validate_answer(self, answer: Optional[str]) -> List[str]:
        if not answer:
            return []
        # TODO Implement the answer validation
        return []
