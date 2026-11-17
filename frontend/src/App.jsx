import React, { useState } from "react";

import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function App() {

    const [token, setToken] = useState(
        sessionStorage.getItem("token")
    );

    const handleLogin = (newToken) => {

        setToken(newToken);

    };

    const handleLogout = () => {

        sessionStorage.removeItem("token");
        sessionStorage.removeItem("name");

        setToken(null);

    };

    return (

        <div>

            {token ? (

                <Dashboard onLogout={handleLogout} />

            ) : (

                <Login onLogin={handleLogin} />

            )}

        </div>

    );

}

export default App;