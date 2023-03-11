import { Flex, Button, Text } from "@mantine/core"
import Row from './AccountRow'
import { useContext, useEffect, useState } from "react"
import AuthContext from "../Context"
import baseUrl from "../baseUrl"
import { showNotification } from "@mantine/notifications"
import serverErrorNotification from "../serverErrorNotification"

function Account() {
    const auth = useContext(AuthContext)

    const [username, setUsername] = useState("")
    const [firstName, setFirstName] = useState("")
    const [lastName, setLastName] = useState("")
    const [email, setEmail] = useState("")
    const [phone, setPhone] = useState("")

    useEffect(async () => {
        if (auth.token === null) {
            return
        }

        fetch(baseUrl + 'account/', {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${auth.token}`
            }
        })
        .catch(() => showNotification(serverErrorNotification))
        .then(response => {
            switch (response.status) {
                case 401:
                    w                 w 
            }
            if (!response.ok) {
                return Promise.reject()
            }

            return response.json()
        })
        .catch(() => Promise.reject())
        .then(data => {
            setUsername(data.username)
            setFirstName(data.first_name)
            setLastName(data.last_name)
            setEmail(data.email)
            setPhone(data.phone)
        })
        .catch(() => {})
    }, [auth.token])

    function Content() {
        if (auth.token === null) {
            return <Text style={{marginTop: 20}}>You are not logged in!</Text>
        }

        if (username === "") {
            return <Text style={{marginTop: 20}}>Account data isn't loaded.</Text>
        }

        return <>
            <Row label="Username:" value={username} />
            <Row label="First name:" value={firstName} />
            <Row label="Last name:" value={lastName} />
            <Row label="Email:" value={email} />
            <Row label="Phone number:" value={phone} />
            <Row label="Password:" value="********" />
            <Button color="red" onClick={() => auth.setToken(null)} >
                Delete account
            </Button>
        </>
    }

    return (
        <Flex
            direction="column"
            align="center"
            gap="xs"
        >
            <Content />
        </Flex>
    )
}

export default Account