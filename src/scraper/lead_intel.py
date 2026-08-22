from __future__ import annotations

from .models import LeadProfile, LeadSignal, OfferScore, PageSnapshot

BOOKING_TERMS = (
    "book online",
    "schedule online",
    "book appointment",
    "schedule appointment",
    "request appointment",
)
CHAT_TERMS = ("live chat", "chat with us", "chat now", "message us")
AFTER_HOURS_TERMS = ("24/7", "24 hour", "24-hour", "emergency service", "after hours")
HIGH_INTENT_TERMS = (
    "call now",
    "call today",
    "free estimate",
    "request a quote",
    "same day",
    "same-day",
)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _signal(
    snapshot: PageSnapshot,
    *,
    kind: str,
    label: str,
    rationale: str,
    delta: int,
    confidence: float,
) -> LeadSignal:
    return LeadSignal(
        kind=kind,
        label=label,
        rationale=rationale,
        score_delta=delta,
        confidence=confidence,
        evidence=snapshot.evidence,
    )


def audit_lead(snapshot: PageSnapshot) -> LeadProfile:
    text = snapshot.text
    signals: list[LeadSignal] = []

    has_phone = bool(snapshot.phone_links)
    has_booking = _contains_any(text, BOOKING_TERMS)
    has_chat = _contains_any(text, CHAT_TERMS)
    has_after_hours = _contains_any(text, AFTER_HOURS_TERMS)
    has_high_intent = _contains_any(text, HIGH_INTENT_TERMS)
    has_viewport = bool(snapshot.metadata.get("has_viewport_meta"))
    has_description = bool(snapshot.metadata.get("meta_description"))

    if has_phone:
        signals.append(
            _signal(
                snapshot,
                kind="phone_conversion",
                label="Phone-dependent conversion path",
                rationale="The public site exposes one or more click-to-call links.",
                delta=18,
                confidence=0.95,
            )
        )
    if has_after_hours:
        signals.append(
            _signal(
                snapshot,
                kind="after_hours_demand",
                label="After-hours or emergency demand",
                rationale="The site advertises 24-hour, emergency, or after-hours availability.",
                delta=22,
                confidence=0.9,
            )
        )
    if has_phone and not has_booking:
        signals.append(
            _signal(
                snapshot,
                kind="no_online_booking",
                label="No obvious online booking language",
                rationale=(
                    "A phone path was observed but common online booking language "
                    "was not found on the page."
                ),
                delta=16,
                confidence=0.7,
            )
        )
    if has_phone and not has_chat:
        signals.append(
            _signal(
                snapshot,
                kind="no_live_chat",
                label="No obvious live-chat path",
                rationale=(
                    "A phone path was observed but common live-chat language "
                    "was not found on the page."
                ),
                delta=8,
                confidence=0.65,
            )
        )
    if has_high_intent:
        signals.append(
            _signal(
                snapshot,
                kind="high_intent_cta",
                label="High-intent acquisition language",
                rationale=(
                    "The page contains conversion language such as call-now, quote, "
                    "or same-day service."
                ),
                delta=12,
                confidence=0.85,
            )
        )
    if snapshot.forms == 0:
        signals.append(
            _signal(
                snapshot,
                kind="no_form",
                label="No HTML form detected",
                rationale="No standard form element was found in the fetched page HTML.",
                delta=7,
                confidence=0.8,
            )
        )
    if not has_viewport:
        signals.append(
            _signal(
                snapshot,
                kind="mobile_foundation",
                label="Missing viewport metadata",
                rationale="The fetched HTML does not expose a standard viewport meta tag.",
                delta=20,
                confidence=0.95,
            )
        )
    if not has_description:
        signals.append(
            _signal(
                snapshot,
                kind="seo_foundation",
                label="Missing meta description",
                rationale="The fetched page does not expose a standard meta description.",
                delta=10,
                confidence=0.9,
            )
        )

    voice_score = min(
        100,
        15
        + sum(
            signal.score_delta
            for signal in signals
            if signal.kind
            in {
                "phone_conversion",
                "after_hours_demand",
                "no_online_booking",
                "no_live_chat",
                "high_intent_cta",
            }
        ),
    )
    website_score = min(
        100,
        10
        + sum(
            signal.score_delta
            for signal in signals
            if signal.kind in {"no_form", "mobile_foundation", "seo_foundation"}
        ),
    )
    automation_score = min(
        100,
        10
        + (18 if has_high_intent else 0)
        + (15 if has_phone and not has_booking else 0)
        + (10 if snapshot.forms > 0 else 0),
    )

    confidence = 0.0
    if signals:
        confidence = round(sum(s.confidence for s in signals) / len(signals), 3)

    offer_scores = [
        OfferScore(
            offer="voice_ai",
            score=voice_score,
            confidence=confidence,
            explanation=(
                "Ranks observable phone dependence, after-hours demand and "
                "missing self-service paths."
            ),
        ),
        OfferScore(
            offer="website",
            score=website_score,
            confidence=confidence,
            explanation="Ranks basic public website foundation and conversion-path gaps.",
        ),
        OfferScore(
            offer="automation",
            score=automation_score,
            confidence=confidence,
            explanation=(
                "Ranks visible demand and opportunities to automate lead capture "
                "or follow-up."
            ),
        ),
    ]
    best = max(offer_scores, key=lambda item: item.score)

    ranked_signals = sorted(signals, key=lambda item: item.score_delta, reverse=True)
    why_now_parts = [signal.label for signal in ranked_signals[:3]]
    hostname = (snapshot.url.host or "").removeprefix("www.")

    return LeadProfile(
        domain=hostname,
        url=snapshot.url,
        business_name=snapshot.title,
        signals=signals,
        offer_scores=offer_scores,
        confidence=confidence,
        evidence=snapshot.evidence,
        recommended_offer=best.offer,
        why_now=(
            "; ".join(why_now_parts)
            if why_now_parts
            else "No strong public signal detected."
        ),
    )
