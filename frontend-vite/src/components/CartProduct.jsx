import { Flex, Image, NumberInput, Button, Text } from "@mantine/core"
import { useContext } from "react"
import Context from "../Context"

function CartProduct(props) {
    const context = useContext(Context)

    const remove = () => {
        context.setCart(products => {
            const newCart = products.filter(p => p.id !== props.id)
            window.localStorage.setItem("cart", JSON.stringify(newCart))
            return newCart
        })
    }

    return (
        <Flex
            direction="row"
            wrap="nowrap"
            align="center"
            gap="xl"
            justify="space-between"
            style={{width: "100%"}}
        >
            {props.name 
            ? <Flex direction="column" wrap="nowrap" gap="xs" style={{width: "20%"}}>
                <Image src={props.img} alt="product photo" width="100%" />
                <Text>{props.name}</Text>
              </Flex>
            : <Text align="center" style={{width: "20%"}}>Product</Text>}
            {props.amount 
            ? <NumberInput defaultValue={props.amount} label="Amount" style={{width: "20%"}} />
            : <Text align="center"  style={{width: "20%"}}>Amount</Text>}
            {props.price
            ? <Text align="center"  style={{width: "20%"}}>{props.price}$</Text>
            : <Text align="center"  style={{width: "20%"}}>Price</Text>}
            {props.price
            ? <Text align="center"  style={{width: "20%"}}>{props.price}$</Text>
            : <Text align="center"  style={{width: "20%"}}>Total</Text>}
            {props.name 
            ? <Button color="red" style={{width: "20%"}} onClick={remove}>Delete</Button>
            : <div style={{width: "20%"}} />}
        </Flex>
    )
}

export default CartProduct