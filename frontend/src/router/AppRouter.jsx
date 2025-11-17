import { Routes, Route, Navigate } from "react-router-dom";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Products from "../pages/Products";
import StockMovements from "../pages/StockMovements";
import Warehouses from "../pages/Warehouses";
import Users from "../pages/Users";
import Profile from "../pages/Profile";
import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";
import ExpiringStock from "../pages/ExpiringStock";
import MovementList from "../pages/MovementList";
import MovementDetail from "../pages/MovementDetail";
import ProductList from "../pages/ProductList";
import ProductDetail from "../pages/ProductDetail";
import AdminRoute from "./AdminRoute";
import NewProduct from "../pages/NewProduct";
import EditProduct from "../pages/EditProduct";
import ProductStock from "../pages/ProductStock";
import ProductHistory from "../pages/ProductHistory";
import Categories from "../pages/Categories";
import CreateMovement from "../pages/CreateMovement";
import WarehouseList from "../pages/WarehouseList";
import NewWarehouse from "../pages/NewWarehouse";
import WarehouseDetail from "../pages/WarehouseDetail";
import EditWarehouse from "../pages/EditWarehouse";
import ProductStockByWarehouse from "../pages/ProductStockByWarehouse";
import WarehouseStock from "../pages/WarehouseStock";
import WarehouseStockHistory from "../pages/WarehouseStockHistory";
import ProductHistoryByWarehouse from "../pages/ProductHistoryByWarehouse";
import NewUser from "../pages/NewUser";
import EditUser from "../pages/EditUser";

/*
Routes and Route come from react-router-dom and allow defining the app's routes (similar to a switch-case).
Navigate is used to redirect from one route to another.
*/

export default function AppRouter() {
  return (
    // Inside <Routes>, we place the <Route> elements that represent different pages.
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />

      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<AdminRoute />}>
        <Route path="/users" element={<Users />} />
        <Route path="/users/new" element={<NewUser />} />
        <Route path="/users/:id/edit" element={<EditUser />} />
        <Route path="/products/new" element={<NewProduct />} />
        <Route path="/products/:id/edit" element={<EditProduct />} />
        <Route path="/warehouses/new" element={<NewWarehouse />} />
        <Route path="/warehouses/:id/edit" element={<EditWarehouse />} />
        <Route path="/categories" element={<Categories />} />
      </Route>

      <Route element={<PrivateRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/stock-movements" element={<StockMovements />} />
        <Route path="/warehouses" element={<Warehouses />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/expiring" element={<ExpiringStock />} />
        <Route path="/stock-movements/new" element={<CreateMovement />} />
        <Route path="/stock-movements/list" element={<MovementList />} />
        <Route path="/stock-movements/:id" element={<MovementDetail />} />
        <Route path="/products/list" element={<ProductList />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/products/:id/stock" element={<ProductStock />} />
        <Route path="/products/:id/history" element={<ProductHistory />} />
        <Route
          path="/stock/warehouse/:warehouse_id/products/:product_id/history"
          element={<ProductHistoryByWarehouse />}
        />
        <Route path="/warehouses/list" element={<WarehouseList />} />
        <Route path="/warehouses/:id" element={<WarehouseDetail />} />
        <Route
          path="/stock/warehouse/:warehouse_id/product/:product_id"
          element={<ProductStockByWarehouse />}
        />
        <Route
          path="/stock/warehouse/:warehouse_id"
          element={<WarehouseStock />}
        />
        <Route
          path="/stock/warehouse/:warehouse_id/history"
          element={<WarehouseStockHistory />}
        />
      </Route>
    </Routes>
  );
}
