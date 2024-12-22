import { ReactNode } from "react";

import "./input-with-icon.css";

type ElementProps = {
    children: ReactNode,
    className: string,
    placeholder: string,
    type: string
}

function InputWithIcon({ children, className, placeholder, type }: ElementProps) {
    return (
        <div className="input-with-icon">
            <input className={className} type={type} placeholder={placeholder} />
            {children}
        </div>
    );
}

export default InputWithIcon;