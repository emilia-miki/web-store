import { Button, Container, Flex, Image, Text } from "@mantine/core"
import { useContext, useEffect, useState } from "react"
import baseUrl from "../baseUrl"
import { showNotification } from "@mantine/notifications"
import Context from "../Context"
import { useParams } from "react-router-dom"

function ProductDetails() {
    const [found, setFound] = useState(false)
    const [name, setName] = useState("")
    const alt = `Photo of ${name}`
    const [description, setDescription] = useState("")
    const [img, setImg] = useState("")
    const [price, setPrice] = useState("")
    const [left, setLeft] = useState(0)

    const descriptionElement = <>
        {description.split('\n').map(line => <Text key={line}>{line}</Text>)}
    </>

    const context = useContext(Context)
    const { id } = useParams()
    const isInCart = context.cart.map(obj => obj.id).includes(id)

    const addToCart = () => {
        context.setCart(cart => {
            const newCart = [...cart, {
                id,
                name,
                img,
                price,
                left
            }]
            window.localStorage.setItem("cart", JSON.stringify(newCart))
            return newCart
        })
    }

    const removeFromCart = () => {
        context.setCart(cart => {
            const newCart = cart.filter(obj => obj.id !== id)
            window.localStorage.setItem("cart", JSON.stringify(newCart))
            return newCart
        })
    }

    let availability, color
    if (left === 0) {
        availability = "Not in stock"
        color = "red"
    } else if (left <= 10) {
        availability = `Only ${left} left!`
        color = "yellow"
    } else {
        availability = "Available"
        color = "green"
    }

    useEffect(() => {
        fetch(baseUrl + `products/${id}`)
        .then(response => {
            if (!response.ok) {
                return Promise.reject()
            }

            return response.json()
        })
        .catch(err => {
            if (err) {
                showNotification({
                    title: "Server error",
                    message: "Could not connect to the server",
                    color: "red"
                })
            }

            return Promise.reject()
        })
        .then(data => {
            setName(data.name)
            setDescription(data.description)
            setImg(data.img)
            setPrice(data.price)
            setLeft(data.left)

            setFound(true)
        })
        .catch(() => {})
    }, [id])

    return (
        <Flex
            direction="row"
            justify="space-around"
            wrap="nowrap"
        >
            {
                found
                ? <>
                    <Flex
                        direction="column"
                        wrap="nowrap"
                        justify="center"
                        style={{
                            width: "33%",
                            padding: 0,
                            margin: 0
                        }}
                    >
                        <Image width="100%" src={img} alt={alt} />
                    </Flex>
                    <Flex
                        direction="column"
                        gap="xs"
                        justify="center"
                        style={{
                            width: "33%"
                        }}
                    >
                        <Text size={16} style={{marginRight: "auto"}}>{name}</Text>
                        <Text size={16} style={{marginRight: "auto"}}>{price}</Text>
                        <Text size={14} color={color} style={{marginRight: "auto"}}>{availability}</Text>
                        <Container>{descriptionElement} </Container>
                        {
                            isInCart
                            ? 
                            <Button color="red" onClick={removeFromCart} style={{width: "80%"}}>
                                Remove from cart
                            </Button>
                            : 
                            <Button onClick={addToCart} style={{width: "80%"}}>
                                Add to cart
                            </Button> 
                        }
                    </Flex>                  
                </>
                : <Text style={{marginTop: 20}}>Product not found</Text>
            }
        </Flex>
    )
}

export default ProductDetails