import MicrosoftButton from "./components/MicrosoftButton";
import "./login.css";


export default function LoginPage() {
    /*const navigate = useNavigate();
    const {authenticated} = useAccountDataStore();

    useEffect(() => {
        if(authenticated) navigate("/");
    })*/

    return (
        <div className="login-flexbox">
            <div>
                <div className="login-header">
                    <h1>Events Organiser</h1>
                    <span>You need to log in to use this application</span>
                </div>
                <div className="login-btns">
                    <MicrosoftButton />
                </div>
            </div>
        </div>
    )
}