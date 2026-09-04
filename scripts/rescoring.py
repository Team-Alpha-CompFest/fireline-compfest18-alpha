def apply_rescoring(crpi_original: float, verification_status: str) -> tuple[float, str]:
    """
    crpi_original: skor MURNI dari formula Bagian A (Hazard+Exposure),
    TIDAK PERNAH berubah oleh proses verifikasi apa pun.
    Selalu dihitung ulang dari sini, bukan dari hasil rescoring sebelumnya,
    supaya status verifikasi yang sama selalu menghasilkan skor akhir yang sama.
    """
    multipliers = {
        "verified_severe": 1.2,
        "verified_minor": 0.85,
        "verified_false_alarm": 0.3,
        "pending": 1.0,
    }
    multiplier = multipliers.get(verification_status, 1.0)
    crpi_current = round(min(100, crpi_original * multiplier), 1)
    return crpi_current, verification_status