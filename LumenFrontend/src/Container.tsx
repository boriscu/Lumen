import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./router";
import { useEffect, useState } from "react";
import { Grid, CircularProgress } from "@mui/material";

const Container = () => {
  const [initialLoad, setInitialLoad] = useState(true);
  useEffect(() => {
    if (initialLoad) {
      setTimeout(() => {
        setInitialLoad(false);
      }, 2000);
    }
  }, [initialLoad]);
  if (initialLoad) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Grid
          container
          direction="column"
          alignItems="center"
          justifyContent="center"
          spacing={10}
        >
          <Grid item>
            <img src="/hotel_loading.gif" alt="Logo" className="logo" />
          </Grid>
          <Grid item>
            <CircularProgress sx={{ color: "#e0e4fc" }} />
          </Grid>
        </Grid>
      </div>
    );
  }
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
};

export default Container;
