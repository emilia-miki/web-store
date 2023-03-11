import { Flex, Text, Button, Modal } from "@mantine/core"
import { useContext, useState } from "react"
import Payment from "./Payment"
import Context from "../Context"
import addDecimals from "../addDecimals"

function Summary() {
    const [opened, setOpened] = useState(false)

    const context = useContext(Context)
    const subtotal = context.cart.map(p => p.price)
                                 .reduce((prev, current) => addDecimals(prev, current))
    const shippingCost = "15.00"
    const total = addDecimals(shippingCost, subtotal)

    return (
        <Flex
            direction="column"
            gap="xs"
            wrap="nowrap"
            sx={(theme) => ({
                width: "30%", 
                alignSelf: "flex-start",
                borderStyle: "solid",
                borderColor: "rgb(214, 217, 220)",
                borderRadius: 3,
                borderWidth: 1,
                padding: 16,
                minWidth: 200,
                '@media (max-width: 860px)': {
                    width: "80%",
                    margin: "auto"
                }
            })}
        >
            <Text weight="bold">Summary</Text>
            <Flex direction="row" justify="space-between">
                <Text>Subtotal:</Text>
                <Text>{subtotal}$</Text>
            </Flex>
            <Flex direction="row" justify="space-between">
                <Text>Shipping cost:</Text>
                <Text>{shippingCost}$</Text>
            </Flex>
            <Flex direction="row" justify="space-between">
                <Text weight="bold">Total:</Text>
                <Text weight="bold">{total}$</Text>
            </Flex>
            <Button onClick={() => setOpened(true)}>Checkout</Button>
            <Modal 
                opened={opened}
                onClose={() => setOpened(false)}
                title="Checkout"
            >
                <Payment />
            </Modal>
        </Flex>
    )
}

export default Summary