import { Button, Flex, Text } from "@mantine/core"
import { Link } from "react-router-dom"
import determineColor from './determineColor'

function Order(props) {
    const color = determineColor(props.status)

    return (
        <Flex
            direction="row"
            align="center"
            justify="space-evenly"
            wrap="nowrap"
            sx={(theme) => ({
                backgroundColor: color,
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
            <Text align="center" style={{width: "20%"}}>{props.id ? `#${props.id}` : "Id"}</Text>
            <Text align="center" style={{width: "20%"}}>{props.date ? props.date.toLocaleDateString() : "Date"}</Text>
            <Text align="center" style={{width: "20%"}}>{props.price ? `${props.price}$` : "Price"}</Text>
            <Text align="center" style={{width: "20%"}}>{props.status ? props.status : "Status"}</Text>
            {props.id
            ? <Button component={Link} to={`/orders/${props.id}`}>Details</Button> 
            : <div style={{width: "84px"}}></div>}
        </Flex>
    )
}

export default Order