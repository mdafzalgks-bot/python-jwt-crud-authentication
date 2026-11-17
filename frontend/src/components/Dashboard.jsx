import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard({ onLogout }) {

    const [customers, setCustomers] = useState([]);

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [age, setAge] = useState("");

    const [editId, setEditId] = useState(null);

    const token = sessionStorage.getItem("token");

    const api = axios.create({
        baseURL: "http://127.0.0.1:5000",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    const fetchCustomers = async () => {

        try {

            const response = await api.get("/customers");

            setCustomers(response.data);

        } catch (error) {

            if (error.response?.status === 401) {
                alert("Session expired. Please login again.");
                onLogout();
            } else {
                alert("Unable to load customers");
            }

        }

    };

    useEffect(() => {

        fetchCustomers();

    }, []);

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            const customer = {
                name,
                email,
                age: Number(age)
            };

            if (editId) {

                await api.put(
                    `/customers/${editId}`,
                    customer
                );

                alert("Customer Updated");

            } else {

                await api.post(
                    "/customers",
                    customer
                );

                alert("Customer Added");

            }

            setName("");
            setEmail("");
            setAge("");
            setEditId(null);

            fetchCustomers();

        } catch (error) {

            alert(
                error.response?.data?.message ||
                "Operation failed"
            );

        }

    };

    const handleEdit = (customer) => {

        setEditId(customer.id);
        setName(customer.name);
        setEmail(customer.email);
        setAge(customer.age);

    };

    const handleDelete = async (id) => {

        if (!window.confirm("Are you sure?")) return;

        try {

            await api.delete(`/customers/${id}`);

            alert("Customer Deleted");

            fetchCustomers();

        } catch (error) {

            alert("Delete failed");

        }

    };

    return (

        <div className="dashboard">

            <div className="topbar">

                <h2>Customer Management</h2>

                <button onClick={onLogout}>
                    Logout
                </button>

            </div>

            <h3>
                Welcome, {sessionStorage.getItem("name")}
            </h3>

            <form onSubmit={handleSubmit}>

                <input
                    type="text"
                    placeholder="Customer Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />

                <input
                    type="email"
                    placeholder="Customer Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <input
                    type="number"
                    placeholder="Age"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                />

                <button type="submit">

                    {editId ? "Update Customer" : "Add Customer"}

                </button>

            </form>

            <h3>Customer Records</h3>

            <table>

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Age</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>

                    {customers.map((customer) => (

                        <tr key={customer.id}>

                            <td>{customer.id}</td>
                            <td>{customer.name}</td>
                            <td>{customer.email}</td>
                            <td>{customer.age}</td>

                            <td>

                                <button
                                    onClick={() => handleEdit(customer)}
                                >
                                    Edit
                                </button>

                                <button
                                    onClick={() => handleDelete(customer.id)}
                                >
                                    Delete
                                </button>

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}

export default Dashboard;