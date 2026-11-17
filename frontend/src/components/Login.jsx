import React, { useState } from "react";
import axios from "axios";

function Login({ onLogin }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [isRegister, setIsRegister] = useState(false);

    const [name, setName] = useState("");

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            if (isRegister) {

                const response = await axios.post(
                    "http://127.0.0.1:5000/register",
                    { username: name, email, password }
                );

                alert(response.data.message);

                setIsRegister(false);

            } else {

                const response = await axios.post(
                    "http://127.0.0.1:5000/login",
                    { email, password }
                );

                sessionStorage.setItem(
                    "token",
                    response.data.token
                );

                sessionStorage.setItem(
                    "name",
                    response.data.username
                );

                onLogin(response.data.token);

            }

        } catch (error) {

            alert(
                error.response?.data?.message ||
                "Something went wrong"
            );

        }

    };

    return (

        <div className="login-container">

            <form onSubmit={handleSubmit} className="login-box">

                <h2>
                    {isRegister ? "Create Account" : "Welcome Back"}
                </h2>

                {isRegister && (

                    <input
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />

                )}

                <input
                    type="email"
                    placeholder="Email Address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button type="submit">

                    {isRegister ? "Register" : "Login"}

                </button>

                <p
                    onClick={() => setIsRegister(!isRegister)}
                    className="toggle"
                >

                    {isRegister
                        ? "Already have an account? Login"
                        : "Don't have an account? Register"}

                </p>

            </form>

        </div>

    );

}

export default Login;