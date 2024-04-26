import { Route, Routes } from "react-router-dom";
import HomePage from "./HomePage/Home";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  );
};

export default AppRoutes;
