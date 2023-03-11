import { Checkbox, MultiSelect, NumberInput, Select, TextInput, Button, Flex } from '@mantine/core'
import serverErrorNotification from '../serverErrorNotification'
import { showNotification } from '@mantine/notifications'
import baseUrl from '../baseUrl'
import { useEffect, useState } from 'react'

const sortingOptions = [
    { value: "name", label: "Name (A - Z)" },
    { value: "-name", label: "Name (Z - A)" },
    { value: "price", label: "Price (cheap to expensive)" },
    { value: "-price", label: "Price (expensive to cheap)" },
]

function Filters(props) {
    const filters = props.filters
    const [requestNeeded, setRequestNeeded] = useState(true)
    const [categoryOptions, setCategoryOptions] = useState([])

    const reset = () => {
        filters.setSearch("")
        filters.setCategories([])
        filters.setLowerPrice(null)
        filters.setUpperPrice(null)
        filters.setOnlyAvailable(false)
        filters.setSortBy("")
    }

    const loadData = () => {
        const params = {}
        if (filters.search && filters.search !== "") {
            params.search = filters.search
        }
        if (filters.categories && filters.categories.length !== 0) {
            params.categories = filters.categories
        }
        if (filters.lowerPrice) {
            params.lower_price = filters.lowerPrice
        }
        if (filters.upperPrice) {
            params.upper_price = filters.upperPrice
        }
        if (filters.onlyAvailable) {
            params.only_available = true
        }
        if (filters.sortBy && filters.sortBy !== "") {
            params.sort_by = filters.sortBy
        }
        if (filters.page !== 1) {
            params.page = filters.page
        }

        fetch(baseUrl + 'products/?' + new URLSearchParams(params))
        .then(response => {
            if (!response.ok) {
                return Promise.reject()
            }

            return response.json()
        })
        .catch(err => {
            if (err) {
                showNotification(serverErrorNotification)
                if (filters.page === 1) {
                    filters.setLoaded(false)
                }
            }

            return Promise.reject()
        })
        .then(data => {
            filters.setLoaded(true)
            if (filters.page === 1) {
                filters.setProducts(data)
            } else {
                filters.setProducts(products => [...products, ...data])
            }
        })
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => loadData(), [requestNeeded, filters.page])
    useEffect(() => {
        fetch(baseUrl + 'categories/')
        .catch(() => showNotification(serverErrorNotification))
        .then(response => response.json())
        .then(data => setCategoryOptions(data))
    })

    return (
        <Flex 
            direction="column"
            wrap="nowrap"
            gap={12}
        >
            <TextInput
                placeholder='Search'
                value={filters.search}
                onChange={filters.setSearch}
            />
            <MultiSelect
                data={categoryOptions}
                placeholder='Categories'
                searchable
                value={filters.categories}
                onChange={filters.setCategories}
            />
            <NumberInput
                placeholder='Lower price'
                hideControls
                value={filters.lowerPrice}
                onChange={filters.setLowerPrice}
            />
            <NumberInput
                placeholder='Upper price'
                hideControls
                value={filters.upperPrice}
                onChange={filters.setUpperPrice}
            />
            <Checkbox
                label="Show only what's in stock"
                value={filters.onlyAvailable}
                onChange={filters.setOnlyAvailable}
            />
            <Select
                data={sortingOptions}
                placeholder='Sort by'
                value={filters.sortBy}
                onChange={filters.setSortBy}
            />
            <Button color="red" onClick={reset}>Reset</Button>
            <Button onClick={() => setRequestNeeded(o => !o)}>Apply</Button>
        </Flex>
    )
}

export default Filters