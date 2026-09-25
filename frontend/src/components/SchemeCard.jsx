import { CaretRight, Plant, PiggyBank, House, Drop, FileText, GraduationCap } from "@phosphor-icons/react";

const CATEGORY_ICONS = {
  agriculture: Plant,
  pension: PiggyBank,
  housing: House,
  water: Drop,
  education: GraduationCap,
};

function getCategoryIcon(category) {
  const key = (category || "").toLowerCase();
  const match = Object.keys(CATEGORY_ICONS).find((k) => key.includes(k));
  return match ? CATEGORY_ICONS[match] : FileText;
}

function SchemeCard({ scheme, onClick, variant = "list" }) {
  const Icon = getCategoryIcon(scheme.category);

  if (variant === "featured") {
    return (
      <button className="scheme-card scheme-card--featured" onClick={onClick}>
        <span className="scheme-card__icon-wrap scheme-card__icon-wrap--featured">
          <Icon size={16} color="var(--color-marigold)" />
        </span>
        <span className="scheme-card__name scheme-card__name--featured">{scheme.scheme_name}</span>
        <span className="scheme-card__meta scheme-card__meta--featured">
          {scheme.category} · {scheme.ministry}
        </span>
        {scheme.financial_benefits && (
          <span className="scheme-card__benefit scheme-card__benefit--featured">{scheme.financial_benefits}</span>
        )}
      </button>
    );
  }

  if (variant === "wide") {
    return (
      <button className="scheme-card scheme-card--wide" onClick={onClick}>
        <span className="scheme-card__icon-wrap scheme-card__icon-wrap--wide">
          <Icon size={17} color="var(--color-marigold)" />
        </span>
        <span className="scheme-card__wide-body">
          <span className="scheme-card__name">{scheme.scheme_name}</span>
          <span className="scheme-card__meta">{scheme.category}</span>
          {scheme.financial_benefits && (
            <span className="scheme-card__benefit">{scheme.financial_benefits}</span>
          )}
        </span>
      </button>
    );
  }

  if (variant === "compact") {
    return (
      <button className="scheme-card scheme-card--grid" onClick={onClick}>
        <span className="scheme-card__icon-wrap">
          <Icon size={13} color="var(--color-ink)" />
        </span>
        <span className="scheme-card__name">{scheme.scheme_name}</span>
        <span className="scheme-card__meta">{scheme.category} · {scheme.ministry}</span>
        {scheme.financial_benefits && (
          <span className="scheme-card__benefit">{scheme.financial_benefits}</span>
        )}
      </button>
    );
  }

  return (
    <button className="scheme-card scheme-card--list" onClick={onClick}>
      <span className="scheme-card__icon-wrap">
        <Icon size={15} color="var(--color-ink)" />
      </span>
      <span className="scheme-card__list-body">
        <span className="scheme-card__name">{scheme.scheme_name}</span>
        <span className="scheme-card__meta">{scheme.category} · {scheme.ministry}</span>
        {scheme.financial_benefits && (
          <span className="scheme-card__list-benefit">{scheme.financial_benefits}</span>
        )}
      </span>
      <CaretRight size={15} color="var(--color-border)" style={{ flexShrink: 0 }} />
    </button>
  );
}

export default SchemeCard;