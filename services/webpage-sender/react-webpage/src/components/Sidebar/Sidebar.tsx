import { ReactNode, ComponentProps } from "react";

import "./sidebar.css"

interface ElementProps extends ComponentProps<"div"> {
    children?: ReactNode
};

function Sidebar({ children, ...props }: ElementProps) {
    return (
        <div className="sidebar" {...props}>
            {children}
        </div>
    )
}

function Header({ children, ...props }: ElementProps) {
    return (
        <div className="sidebar-header" {...props}>
            {children}
        </div>
    );
}

function Content({ children, ...props }: ElementProps) {
    return (
        <div className="sidebar-content" {...props}>
            {children}
        </div>
    );
}

function Footer({ children, ...props }: ElementProps) {
    return (
        <div className="sidebar-footer" {...props}>
            {children}
        </div>
    );
}

export default Object.assign(
    Sidebar,
    {Header, Content, Footer}
);