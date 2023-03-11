import { Flex, Text } from "@mantine/core"
import Product from "./Product"

function Products(props) {
    const filters = props.filters

    const productElements = filters.products.map(
        p => <Product 
                key={p.id} 
                id={p.id} 
                name={p.name} 
                img={p.img} 
                price={p.price} 
                left={p.left} 
             />)

    function Content() {
        if (!filters.loaded) {
            return <Text style={{marginTop: 20}}>Could not load products.</Text>
        }

        if (filters.products.length === 0) {
            return <Text style={{marginTop: 20}}>
                       No products found with the specified filters.
                   </Text>
        }

        return productElements
    }

    return (
        <Flex
            gap="xs"
            justify="space-around"
            align="flex-start"
            direction="row"
            wrap="wrap"
        >
            <Content />
        </Flex>
    )
}

export default Products