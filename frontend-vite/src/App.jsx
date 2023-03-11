import logo from './assets/react.svg'
import Products from './components/Products'
import Filters from './components/Filters'
import Cart from './components/Cart'
import Orders from './components/Orders'
import Account from './components/Account'
import { AppShell, Navbar, Header, Text, Image, Flex, Menu, Button, Modal } from '@mantine/core'
import { Link, Route, BrowserRouter, Routes, Navigate } from 'react-router-dom'
import { useInputState } from '@mantine/hooks'
import { useState, useEffect } from "react"
import menuIcon from './assets/menu-icon.png'
import Register from './components/Register'
import Login from './components/Login'
import Context from './Context'
import ProductDetails from './components/ProductDetails'
import OrderDetails from './components/OrderDetails'
import baseUrl from './baseUrl'

function App() {
  const routeStyle = {
    margin: "auto 8px",
    cursor: "pointer",
    fontWeight: 400,
    whiteSpace: "nowrap"
  }
  const titleStyle = {
    fontWeight: "600", 
    fontSize: "18px", 
    textAlign: "center", 
    width: "100%"
  }

  const [width, setWidth] = useState(window.innerWidth)
  const [menuOpened, setMenuOpened] = useState(false)
  const [registerOpened, setRegisterOpened] = useState(false)
  const [loginOpened, setLoginOpened] = useState(false)
  const [token, setToken] = useState()
  const [cart, setCart] = useState([])
  const breakpoint = 500

  const context = {
    token, 
    setToken,
    refresh: null,
    setRefresh: () => {},
    cart,
    setCart
  }

  context.setRefresh = value => context.refresh = value

  useEffect(() => {
    setToken(window.localStorage.getItem("access"))
    setToken(window.localStorage.getItem("refresh"))
    const storageCart = window.localStorage.getItem("cart")
    if (storageCart) {
      setCart(JSON.parse(storageCart))
    }

    const handleResizeWindow = () => setWidth(window.innerWidth)
    window.addEventListener("resize", handleResizeWindow)
    return () => {
      window.removeEventListener("resize", handleResizeWindow)
    }
  }, [])

  const logout = () => {
    setToken(null)
    context.setRefresh(null)
    window.localStorage.removeItem("access")
    window.localStorage.removeItem("refresh")
  }

  const [search, setSearch] = useInputState("")
  const [categories, setCategories] = useInputState([])
  const [lowerPrice, setLowerPrice] = useInputState(null)
  const [upperPrice, setUpperPrice] = useInputState(null)
  const [onlyAvailable, setOnlyAvailable] = useInputState(false)
  const [sortBy, setSortBy] = useInputState("")
  const [loaded, setLoaded] = useState(false)
  const [products, setProducts] = useState([])
  const [page, setPage] = useState(1)

  const filters = {
    search,
    setSearch,
    categories,
    setCategories,
    lowerPrice,
    setLowerPrice,
    upperPrice,
    setUpperPrice,
    onlyAvailable, 
    setOnlyAvailable,
    sortBy,
    setSortBy,
    loaded,
    setLoaded,
    products,
    setProducts,
    page,
    setPage
  }

  return (
    <BrowserRouter>
      <Context.Provider value={context}>
        <AppShell 
          padding="md"
          navbar={
            <Routes>
              <Route path="/products" element={
                  <Navbar width={{base: 130, xs: 200, sm: 260}} height={500} p="xs">
                    <Filters filters={filters} />
                  </Navbar>
                } 
              />
              <Route path="*" element={<></>} />
            </Routes>
          }
          header={
            <Header height={60} p="xs" style={{padding: "0"}}>
              <Flex
                direction="row"
                wrap="nowrap"
                align="center"
                style={{padding: "0 16px", height: "100%"}}
              >
                <Image
                  src={logo}
                  alt="logo"
                  width={40}
                  component={Link}
                  to="/products"
                  style={{marginRight: "auto"}}
                />
                <Routes>
                  <Route path="/products" element={<Text style={titleStyle}>Our products</Text>} />
                  <Route path="/account" element={<Text style={titleStyle}>Your account</Text>} />
                  <Route path="/orders" element={<Text style={titleStyle}>Your orders</Text>} />
                  <Route path="/cart" element={<Text style={titleStyle}>Your cart</Text>} />
                  <Route path="*" element={<></>} />
                </Routes>
                {
                  width < breakpoint
                  ? <>
                      <Menu shadow="md" width={200} onClose={() => setMenuOpened(false)}>
                      <Menu.Target>
                        <Button 
                          onClick={() => setMenuOpened(!menuOpened)}
                          style={{
                            padding: "2px 6px", 
                            backgroundColor: "transparent",
                            rotate: menuOpened ? "-90deg" : "0deg",
                            transition: "all 0.2s ease"
                          }}
                        >
                          <Image 
                            src={menuIcon}
                            alt="navigation menu icon" 
                            width={30} 
                            height={30} 
                          />
                        </Button>
                      </Menu.Target>

                      <Menu.Dropdown>
                        <Menu.Item component={Link} to="/products">Products</Menu.Item>
                          {
                            token === null
                            ? <>
                              <Menu.Item
                                onClick={() => setRegisterOpened(true)}>Register</Menu.Item>
                              <Menu.Item
                                onClick={() => setLoginOpened(true)}>Log in</Menu.Item>
                              <Menu.Item component={Link} to="/cart">Cart</Menu.Item>
                            </>
                            : <>
                              <Menu.Item component={Link} to="/account">Account</Menu.Item>
                              <Menu.Item
                                onClick={logout}
                              >
                                Log out
                              </Menu.Item>
                              <Menu.Item component={Link} to="/orders">Orders</Menu.Item>
                              <Menu.Item component={Link} to="/cart">Cart</Menu.Item>
                            </>
                          }
                      </Menu.Dropdown>
                    </Menu>
                  </>
                  : <>
                    <Text component={Link} to="/products" style={routeStyle}>Products</Text>
                      {
                        token === null
                        ? <>
                          <Text 
                            onClick={() => setRegisterOpened(true)} 
                            style={routeStyle}
                          >
                            Register
                          </Text>
                          <Text 
                            onClick={() => setLoginOpened(true)} 
                            style={routeStyle}
                          >
                            Log in
                          </Text>
                          <Text component={Link} to="/cart" style={routeStyle}>Cart</Text>     
                        </>
                        : <>
                          <Text component={Link} to="/account" style={routeStyle}>Account</Text>  
                          <Text 
                            onClick={logout}
                            style={routeStyle}
                          >
                            Log out
                          </Text> 
                          <Text component={Link} to="/orders" style={routeStyle}>Orders</Text>
                          <Text component={Link} to="/cart" style={routeStyle}>Cart</Text>     
                        </>
                      }
                  </>
                }
              </Flex>
            </Header>
          }
        >
          <Modal 
            title="Register" 
            opened={registerOpened} 
            onClose={() => {
              setRegisterOpened(false)
              setMenuOpened(false)
            }}
          >
            <Register callback={() => setRegisterOpened(false)} />
          </Modal>
          <Modal
            title="Log in"
            opened={loginOpened}
            onClose={() => {
              setLoginOpened(false)
              setMenuOpened(false)
            }}
          >
            <Login callback={() => setLoginOpened(false)} />
          </Modal>
          <Routes>
            <Route path="/" element={<Navigate to="/products" replace />} />
            <Route path="/products">
              <Route index element={<Products filters={filters} />} />
              <Route path=":id" element={<ProductDetails />} />
            </Route>
            <Route path="/account" element={<Account />} />
            <Route path="/orders">
              <Route index element={<Orders />} />
              <Route path=":id" element={<OrderDetails />} />
            </Route>
            <Route path="/cart" element={<Cart />} />
          </Routes>
        </AppShell> 
      </Context.Provider>
    </BrowserRouter>  
  )
}

export default App
