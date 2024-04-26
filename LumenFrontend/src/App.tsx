import React from "react";
import "./App.css";
import { SnackbarProvider } from "notistack";
import Container from "./Container";
import { QueryClientProvider, QueryClient, setLogger } from "react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      cacheTime: 15 * 60 * 1000,
      staleTime: 0 * 60 * 1000,
      retry: false,
    },
  },
});

setLogger({
  log: () => {},
  warn: () => {},
  error: () => {},
});

function App() {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "center",
          }}
        >
          <Container />
        </SnackbarProvider>
      </QueryClientProvider>
    </React.StrictMode>
  );
}

export default App;
