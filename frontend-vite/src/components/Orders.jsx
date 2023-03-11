import { Flex, Text } from "@mantine/core"
import Order from './Order'
import AuthContext from "../Context"
import { useContext, useEffect, useState } from "react"
import baseUrl from "../baseUrl"
import { showNotification } from "@mantine/notifications"
import serverErrorNotification from "../serverErrorNotification"

function Orders() {
    const auth = useContext(AuthContext)

    const [orders, setOrders] = useState([])
    const [loaded, setLoaded] = useState(false)

    const orderElements = orders.map(
        o => <Order key={o.id} id={o.id} date={new Date(o.date)} price={o.price} status={o.status} />)

    useEffect(async () => {
        const response = await fetch(baseUrl + 'orders/', {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${auth.token}`
            }
        })
        .catch(() => {
            showNotification(serverErrorNotification)
            setLoaded(false)
        })
        if (response.ok) {
            response.json().then(data => {
                setLoaded(true)
                setOrders(data)
            })
        } else {
            response = await fetch(baseUrl + 'token/refresh/', {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${auth.refresh}`
                }
            }).catch(() => {
                showNotification(serverErrorNotification)
                setLoaded(false)
            })
            response.json().then(data => {
                auth.setToken(data.access)
            }).catch(() => {
                showNotification(serverErrorNotification)
                setLoaded(false)
            })
            response = await fetch(baseUrl + 'orders/', {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${auth.token}`
                }
            }).catch(() => {
                showNotification(serverErrorNotification)
                setLoaded(false)
            })
            response.json().then(data => {
                setLoaded(true)
                setOrders(data)
            })
        }
    }, [auth.token])

    function Content() {
        if (auth.token === null) {
            return <Text style={{marginTop: 20}}>You are not logged in!</Text>
        }

        if (!loaded) {
            return <Text style={{marginTop: 20}}>Could not load orders.</Text>
        }

        if (orderElements.length === 0) {
            return <Text style={{marginTop: 20}}>You have no orders.</Text>
        }

        return (
            <>
                <Order />
                {orderElements}
            </>
        )
    }

    return (
        <Flex 
            direction="column"
            gap="md"
            align="center"
        >
            <Content />
        </Flex>
    )
}

export default Orders