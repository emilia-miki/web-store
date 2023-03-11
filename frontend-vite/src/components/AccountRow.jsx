import { Flex, Text, Button } from '@mantine/core'

function Row(props) {
    return (
        <Flex
            direction="row"
            align="center"
            justify="space-between"
            gap="xl"
            sx={(theme) => ({
                borderStyle: "solid",
                borderColor: "rgb(214, 217, 220)",
                borderWidth: 1,
                borderRadius: 3,
                padding: 8,
                width: "80%",
                [`@media (min-width: ${theme.breakpoints.sm}px)`]: {
                    width: "60%"
                },
                [`@media (min-width: ${theme.breakpoints.md}px)`]: {
                    width: "40%"
                }
            })}
        >
            <Flex direction="column" align="flex-start" justify="center">
                <Text weight="bold">{props.label}</Text>
                <Text>{props.value}</Text>
            </Flex>
            <Button>Edit</Button>
        </Flex>
    )
}

export default Row