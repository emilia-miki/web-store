import { Text, Image, Flex } from '@mantine/core'
import { Link } from 'react-router-dom'

function Product(props) {
    let alt = `Photo of ${props.name}`

    let availability, color
    if (props.left === 0) {
        availability = "Not in stock"
        color = "red"
    } else if (props.left <= 10) {
        availability = `Only ${props.left} left!`
        color = "yellow"
    } else {
        availability = "Available"
        color = "green"
    }

    return (
        <Flex
            direction="column"
            wrap="nowrap"
            sx={(theme) => ({
                width: "48%",
                padding: 0,
                margin: 0,
                [`@media (min-width: ${theme.breakpoints.sm}px)`]: {
                    width: "33%"
                },
                [`@media (min-width: ${theme.breakpoints.md}px)`]: {
                    width: "24%"
                }
            })}
        >
            <Image width="100%" src={props.img} alt={alt} 
                style={{cursor: "pointer"}} component={Link} to={`/products/${props.id}`} />
            <Text size={16} style={{marginRight: "auto", cursor: "pointer", marginTop: 22}}
                component={Link} to={`/products/${props.id}`}>{props.name}</Text>
            <Text size={16} style={{marginRight: "auto"}}>${props.price}</Text>
            <Text size={14} color={color} 
                style={{marginRight: "auto", marginBottom: 12}}>{availability}</Text>
        </Flex>
    )
}

export default Product