import { Button, Flex, PasswordInput, TextInput } from "@mantine/core"
import { useContext, useState } from "react"
import { useInputState } from "@mantine/hooks"
import baseUrl from "../baseUrl"
import Context from "../Context"
import { showNotification } from "@mantine/notifications"
import serverErrorNotification from "../serverErrorNotification"

function Login(props) {
    const [username, setUsername] = useInputState("")
    const [password, setPassword] = useInputState("")
    const [valid, setValid] = useState(true)

    const context = useContext(Context)

    const makeRequest = () => {
        fetch(baseUrl + 'token/', {
            method: 'POST',
            body: JSON.stringify({
                username, 
                password
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                setValid(false)
                return Promise.reject()
            }

            setValid(true)
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
    }

    return (
        <Flex
            direction="column"
            gap="md"
            align="center"
            style={{marginTop: 20}}
        >
            <TextInput placeholder="Username" style={{width: "80%"}} 
                value={username} onChange={setUsername}
                error={(!valid && "Invalid credentials") 
                       || (username === "" && "This field is required")} />
            <PasswordInput placeholder="Password" style={{width: "80%"}} 
                value={password} onChange={setPassword}
                error={(!valid && "Invalid credentials")
                       || (password === "" && "This field is required")} />
            <Button onClick={makeRequest} autoFocus>Log in</Button>
        </Flex>
    )
}

export default Login