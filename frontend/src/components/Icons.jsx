// Small line icons, one per signal source. Decorative: always paired with text.
const common = {
  viewBox: "0 0 20 20",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export const BehaviorIcon = (p) => (
  <svg {...common} {...p}>
    <path d="M4 16v-3M10 16V9M16 16V4" />
  </svg>
);

export const ContentIcon = (p) => (
  <svg {...common} {...p}>
    <rect x="3" y="3" width="6" height="6" rx="1.2" />
    <rect x="11" y="3" width="6" height="6" rx="1.2" />
    <rect x="3" y="11" width="6" height="6" rx="1.2" />
    <rect x="11" y="11" width="6" height="6" rx="1.2" strokeDasharray="2 2" />
  </svg>
);

export const SessionIcon = (p) => (
  <svg {...common} {...p}>
    <circle cx="5" cy="10" r="2.4" />
    <circle cx="15" cy="5" r="2.4" />
    <circle cx="15" cy="15" r="2.4" />
    <path d="M7.2 9 12.8 6M7.2 11l5.6 3" />
  </svg>
);

export const WordsIcon = (p) => (
  <svg {...common} {...p}>
    <path d="M3.5 5.5h13M3.5 10h9M3.5 14.5h6" />
    <path d="M14 13l2 2 3-4" />
  </svg>
);

export const ArrowIcon = (p) => (
  <svg {...common} {...p}>
    <path d="M4 10h12M12 6l4 4-4 4" />
  </svg>
);

export const CheckIcon = (p) => (
  <svg {...common} {...p}>
    <path d="M5 10.5 8.5 14 15 6.5" />
  </svg>
);
