import MicrosoftIcon from "@/assets/ms-symbollockup_mssymbol_19.svg";
import { TailSpin } from 'react-loading-icons'
import { useState } from "react";
import { getMicrosoftLoginLink } from "@/apis/auth";
import { toast } from "react-toastify"

export default function MicrosoftButton() {
    const [loginInProgress, setLoginInProgress] = useState<boolean>(false);

    const fetchLoginLink = () => {
        if(loginInProgress) return;

        setLoginInProgress(true);
        getMicrosoftLoginLink(
            Intl.DateTimeFormat().resolvedOptions().timeZone
        ).then(result => {
            setLoginInProgress(false);
            window.location.href = result.link!;
        }).catch(err => {
            toast.error("Failed to log in using Microsoft, try again later."); 
            console.error("MS login error: ", err);
        })
    }

    return (
        <button className="ms" onClick={fetchLoginLink}>
            <img src={MicrosoftIcon} />
            <strong>Log in with Microsoft</strong>

            {loginInProgress && <TailSpin style={{height: "1.25em", marginLeft: "1em"}}/>}
        </button>
    )
}