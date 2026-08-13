from __future__ import annotations

from .models import UniversalControl


CONTROL_CATALOG = [
    UniversalControl(control_id="AEGIS-GOV-001", title="Governance and accountability", statement="The organisation defines accountable governance for compliance obligations.", domain="Governance"),
    UniversalControl(control_id="AEGIS-IAM-001", title="Identity and access management", statement="Access to systems and sensitive information is authorised, controlled and periodically reviewed.", domain="Identity & Access Management"),
    UniversalControl(control_id="AEGIS-INC-001", title="Incident and breach management", statement="Security and privacy incidents are identified, managed, escalated and reported within applicable timeframes.", domain="Incident Management"),
    UniversalControl(control_id="AEGIS-PRV-001", title="Privacy governance", statement="Personal data processing is governed by documented privacy principles, notices and lawful processing rules.", domain="Privacy"),
    UniversalControl(control_id="AEGIS-RGT-001", title="Data subject rights", statement="Individuals can exercise applicable rights over their personal data through defined processes.", domain="Data Subject Rights"),
    UniversalControl(control_id="AEGIS-RSK-001", title="Risk assessment", statement="Compliance, security and privacy risks are assessed and treated using documented methods.", domain="Risk Management"),
    UniversalControl(control_id="AEGIS-TRN-001", title="Awareness and training", statement="Personnel receive role-appropriate compliance, privacy and security training.", domain="People & Training"),
    UniversalControl(control_id="AEGIS-TPR-001", title="Third-party governance", statement="Third parties are assessed, contracted and monitored against applicable control requirements.", domain="Third Party Risk"),
    UniversalControl(control_id="AEGIS-AUD-001", title="Audit and assurance", statement="Compliance controls and evidence are periodically reviewed and independently assured where required.", domain="Audit & Assurance"),
    UniversalControl(control_id="AEGIS-CRY-001", title="Cryptographic protection", statement="Sensitive information is protected using appropriate cryptographic controls where required.", domain="Data Security"),
    UniversalControl(control_id="AEGIS-RET-001", title="Retention and disposal", statement="Information is retained only as required and securely disposed when retention expires.", domain="Information Lifecycle"),
    UniversalControl(control_id="AEGIS-RPT-001", title="Regulatory reporting", statement="Required regulatory reports, returns and notifications are prepared, approved and submitted on time.", domain="Regulatory Reporting"),
]


CONTROL_KEYWORDS: dict[str, set[str]] = {
    "AEGIS-GOV-001": {"governance", "board", "management", "policy", "accountable", "officer", "responsible"},
    "AEGIS-IAM-001": {"access", "account", "identity", "privileged", "authentication", "authorisation", "authorization", "password"},
    "AEGIS-INC-001": {"incident", "breach", "notify", "notification", "response", "72 hours", "security event"},
    "AEGIS-PRV-001": {"privacy", "personal data", "lawful", "consent", "notice", "processing"},
    "AEGIS-RGT-001": {"data subject", "access request", "rectification", "erasure", "portability", "complaint"},
    "AEGIS-RSK-001": {"risk", "impact assessment", "dpia", "assessment", "mitigation"},
    "AEGIS-TRN-001": {"training", "awareness", "sensitisation", "personnel", "staff"},
    "AEGIS-TPR-001": {"third party", "third-party", "processor", "vendor", "supplier", "contract"},
    "AEGIS-AUD-001": {"audit", "assurance", "review", "inspection", "assessment return"},
    "AEGIS-CRY-001": {"encrypt", "encryption", "cryptographic", "key management"},
    "AEGIS-RET-001": {"retention", "retain", "dispose", "deletion", "delete", "archive"},
    "AEGIS-RPT-001": {"report", "return", "submit", "filing", "regulator", "commission", "deadline"},
}
