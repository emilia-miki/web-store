import { Flex, Button, TextInput, NumberInput } from "@mantine/core"

function Payment(props) {
    return (
        <Flex 
            direction="column"
            wrap="nowrap"
            gap="md"
            style={props.style}
        >
            <TextInput placeholder="First Name" />
            <TextInput placeholder="Last Name" />
            <TextInput placeholder="Phone number" />
            <TextInput placeholder="Email" />
            <TextInput placeholder="Shipping address" />
            <NumberInput placeholder="Credit card number" hideControls />
            <Flex direction="row" wrap="nowrap" gap="md">
                <NumberInput placeholder="Expiration date" hideControls />
                <NumberInput placeholder="CVV" hideControls />
            </Flex>
            <Button>Submit</Button>
        </Flex>
    )
}

export default Payment