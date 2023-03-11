import { Flex, Text, Button } from "@mantine/core"
import { useContext, useEffect, useState } from "react"
import baseUrl from "../baseUrl"
import Context from "../Context"
import { showNotification } from "@mantine/notifications"
import OrderProduct from './OrderProduct'
import serverErrorNotification from "../serverErrorNotification"
import { useParams } from "react-router-dom"
import determineColor from "./determineColor"

function OrderDetails() {
    const { id } = useParams()
    const [price, setPrice] = useState()
    const [date, setDate] = useState()
    const [status, setStatus] = useState()
    const [products, setProducts] = useState([])
    const [message, setMessage] = useState("")

    const context = useContext(Context)

    const cancel = () => {
        fetch(baseUrl + `orders/${id}/`, {
            method: "PUT",
            body: JSON.stringify({
                status: "Canceled"
            }),
            headers: {
                "Authorization": `Bearer ${context.token}`,
                "Content-Type": "application/json"
            }
        })
        .catch(() => showNotification(serverErrorNotification))
        .then(response => {
            if (response.ok) {
                setStatus("Canceled")
            }

            return Promise.resolve()
        })
    }

    const productElements = products.map(
        p => <OrderProduct 
                key={p.id} 
                name={p.name}
                img={p.img}
                price={p.price}
                amount={p.amount}
                totalPrice={(Math.round(100 * p.price * p.amount) / 100).toFixed(2)}
             />)

    useEffect(() => {
        if (!id) {
            return
        }

        const fetchProduct = p => fetch(baseUrl + `products/${p.id}`)
                                  .then(response => response.json())
        const resolveProducts = async list => {
            const productPromises = list.map(async p => {
                const newProduct = await fetchProduct(p)
                return {...p, ...newProduct}
            })
            return Promise.all(productPromises)
        }

        fetch(baseUrl + `orders/${id}/`, {
            headers: {
                'Authorization': `Bearer ${context.token}`
            }
        })
        .catch(() => showNotification(serverErrorNotification))
        .then(response => {
            switch (response.status) {
                case 200:
                    setMessage("loaded")
                    return response.json()
                case 401:
                    setMessage("You are not authorized to access this order")
                    return Promise.reject()
                case 404:
                    setMessage("Order not found")
                    return Promise.reject()
                default:
                    showNotification({
                        title: "Error",
                        message: "Unknown server error",
                        color: "red"
                    })
                    return Promise.reject()
            }
        })
        .catch(() => Promise.reject())
        .then(data => {
            setPrice(data.price)
            setDate(new Date(data.date))
            resolveProducts(data.products)
            .then(ps => {
                setProducts(ps)
            })
            setStatus(data.status)
        })
        .catch(() => {})
    }, [context.token])

    return (
        <Flex
            direction="column"
            align="center"
            gap="xl"
            wrap="nowrap"
        >
            {
                message === "loaded"
                ? <>
                    <Flex
                        direction="row"
                        wrap="nowrap"
                        align="center"
                        justify="space-between"
                        sx={theme => ({
                            backgroundColor: determineColor(status),
                            padding: "12px 12px",
                            width: "90%",
                            [`@media (min-width: ${theme.breakpoints.sm}px)`]: {
                                width: "80%"
                            },
                            [`@media (min-width: ${theme.breakpoints.md}px)`]: {
                                width: "60%"
                            },
                            borderRadius: 3
                        })}
                    >
                        <Text>Id: {id}</Text>
                        <Text>Creation time: {date.toLocaleTimeString()} {date.toLocaleDateString()}</Text>
                        <Text>Total price: ${price}</Text>
                        <Text>Status: {status}</Text>
                        {
                            status === "Created"
                            && <Button color="red" onClick={cancel}>Cancel</Button>
                        }
                    </Flex>
                    <Flex
                        direction="row"
                        wrap="wrap"
                        align="flex-start"
                        justify="flex-start"
                        gap="lg"
                        style={{width: "80%"}}
                    >
                        {productElements}
                    </Flex>
                </>
                : <Text>{message}</Text>
            }
        </Flex>
    )
}

export default OrderDetails