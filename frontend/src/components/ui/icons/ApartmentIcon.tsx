const ApartmentIcon = ({ fill = "none", outline = "#000", className = "" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    height={"24px"}
    viewBox="0 0 24 24"
    fill={fill}
    stroke={outline}
    strokeWidth={2}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    {/* Building */}
    <rect x="6" y="3" width="12" height="18" />
    {/* Windows */}
    <line x1="9" y1="6" x2="9" y2="6" />
    <line x1="9" y1="9" x2="9" y2="9" />
    <line x1="9" y1="12" x2="9" y2="12" />
    <line x1="9" y1="15" x2="9" y2="15" />
    <line x1="12" y1="6" x2="12" y2="6" />
    <line x1="12" y1="9" x2="12" y2="9" />
    <line x1="12" y1="12" x2="12" y2="12" />
    <line x1="12" y1="15" x2="12" y2="15" />
    <line x1="15" y1="6" x2="15" y2="6" />
    <line x1="15" y1="9" x2="15" y2="9" />
    <line x1="15" y1="12" x2="15" y2="12" />
    <line x1="15" y1="15" x2="15" y2="15" />
    {/* Door */}
    <rect x="11" y="15" width="2" height="6" />
  </svg>
);

export default ApartmentIcon;
