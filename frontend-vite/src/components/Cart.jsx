import { Flex, Text } from "@mantine/core"
import CartProduct from './CartProduct'
import Summary from './Summary'
import Context from "../Context"
import { useContext } from "react"

function Cart() {
    const context = useContext(Context)

    const cartProductElements = context.cart.map(
        p => <CartProduct 
                key={p.id} 
                id={p.id} 
                name={p.name} 
                img={p.img} 
                amount={p.amount} 
                price={p.price} 
             />)

    function Conditional() {
        if (cartProductElements.length === 0) {
            return <Text>Your cart is empty</Text>
        }

        if (context.token) {
            return <Summary />
        }

        return <Text>You have to be logged in to place an order.</Text>
    }

    return (
        <>
            <Flex
                direction="row"
                wrap="wrap"
                align="center"
                justify="space-between"
                gap="xl"
                style={{width: "100%", padding: "20px 40px"}}
            >
                {
                    cartProductElements.length !== 0
                    ? <>
                        <Flex
                            direction="column"
                            wrap="nowrap"
                            align="center"
                            gap="md"
                            sx={() => ({
                                minWidth: 500,
                                maxWidth: "60%",
                                margin: "auto",
                                '@media (max-width: 860px)': {
                                    width: "100%"
                                }
                            })}
                        >
                            <CartProduct />
                            {cartProductElements}
                        </Flex>
                        <Conditional />
                    </>
                    : <Text style={{margin: "auto"}}>Your cart is empty</Text>
                }
            </Flex>
        </>
    )
}

export default Cart