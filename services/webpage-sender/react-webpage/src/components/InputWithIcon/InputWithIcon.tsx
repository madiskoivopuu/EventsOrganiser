import { ReactNode } from "react";

import "./input-with-icon.css";

type ElementProps = {
    children: ReactNode,
    className: string,
    placeholder?: string,
    type: string,
    onClick?: () => void
}

function InputWithIcon({ children, className, placeholder, type, onClick }: ElementProps) {
    return (
        <div className="input-with-icon">
            <input className={className} type={type} placeholder={placeholder} onClick={onClick} />
            {children}
        </div>
    );
}

export default InputWithIcon;