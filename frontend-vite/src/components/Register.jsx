import { Button, Flex, PasswordInput, TextInput } from "@mantine/core"
import { useInputState } from "@mantine/hooks"
import { useContext } from "react"
import baseUrl from "../baseUrl"
import Context from "../Context"
import { showNotification } from "@mantine/notifications"
import serverErrorNotification from "../serverErrorNotification"

function Register(props) {
    const [username, setUsername] = useInputState("")
    const [password, setPassword] = useInputState("")
    const [confirmPassword, setConfirmPassword] = useInputState("")
    const passwordsMismatch = password !== confirmPassword
    const [firstName, setFirstName] = useInputState("")
    const [lastName, setLastName] = useInputState("")
    const [email, setEmail] = useInputState("")
    const [phone, setPhone] = useInputState("")

    const context = useContext(Context)

    const makeRequest = () => {
        fetch(baseUrl + 'register/', {
            method: 'POST',
            body: JSON.stringify({
                username, 
                password, 
                "first_name": firstName,
                "last_name": lastName,
                email,
                phone
            }),
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => {
            if (!response.ok) {
                return Promise.reject()
            }

            fetch(baseUrl + 'token/', {
                method: 'POST',
                body: JSON.stringify({
                    username, 
                    password
                }),
                headers: {
                    'Content-Type': "application/json"
                }
            })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject()
                }

                return response.json()
            })
            .catch(err => {
                if (err) {
                    showNotification(serverErrorNotification)
                }

                return Promise.reject()
            })
            .then(data => {
                context.setToken(data.access)
                context.setRefresh(data.refresh)
                window.localStorage.setItem("access", data.access)
                window.localStorage.setItem("refresh", data.refresh)
                props.callback()
            })
            .catch(() => {})
        })
        .catch(err => {
            if (err) {
                showNotification(serverErrorNotification)
            }
        })
    }

    return (
        <Flex
            direction="column"
            gap="md"
            align="center"
            style={{
                marginTop: 20
            }}
        >
            <TextInput placeholder="Username" style={{width: "90%"}} 
                value={username} onChange={setUsername} />
            <PasswordInput placeholder="Password" style={{width: "90%"}} 
                value={password} onChange={setPassword} 
                error={passwordsMismatch && "Passwords do not match"} />
            <PasswordInput placeholder="Confirm password" style={{width: "90%"}} 
                value={confirmPassword} onChange={setConfirmPassword}
                error={passwordsMismatch && "Passwords do not match"} />
            <TextInput placeholder="First Name" style={{width: "90%"}} 
                value={firstName} onChange={setFirstName} />
            <TextInput placeholder="Last Name" style={{width: "90%"}} 
                value={lastName} onChange={setLastName} />
            <TextInput placeholder="Email" style={{width: "90%"}} 
                value={email} onChange={setEmail} />
            <TextInput placeholder="Phone number" style={{width: "90%"}} 
                value={phone} onChange={setPhone} />
            <Button onClick={makeRequest} autoFocus>Register</Button>
        </Flex>
    )
}

export default Register