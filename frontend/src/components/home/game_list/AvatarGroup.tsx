import React from "react";

function AvatarGroup({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex flex-row gap-2">
      {" "}
      <div className="relative flex">
        {React.Children.map(children, (child, index) => (
          <div className={index !== 0 ? "-ml-2" : ""}>{child}</div>
        ))}
      </div>
    </div>
  );
}

export default AvatarGroup;
