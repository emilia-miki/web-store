import { Flex, Image, Text } from "@mantine/core";

function OrderProduct(props) {
    return (
        <Flex
            direction="column"
            gap="sm"
            sx={theme => ({
                width: "46%",
                [`@media (min-width: ${theme.breakpoints.md}px)`]: {
                    width: "18%"
                }
            })}
        >
            <Image src={props.img} alt={`Photo of ${props.name}`} />
            <Text>{props.name}</Text>
            <Text>Price: {props.price}$</Text>
            <Text>Amount: {props.amount}</Text>
            <Text>Total price: {props.totalPrice}</Text>
        </Flex>
    )
}

export default OrderProduct