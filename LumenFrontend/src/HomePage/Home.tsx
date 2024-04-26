import { useState, ChangeEvent } from "react";
import {
  Button,
  CircularProgress,
  Grid,
  IconButton,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { format } from "date-fns";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { PredictResponse } from "../Models/predict";
import { getPredictions } from "../Services/predict";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { Dayjs } from "dayjs";
import { enqueueSnackbar } from "notistack";
import { useCheckFile } from "../Hooks/useCheckFile";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DeleteIcon from "@mui/icons-material/Delete";
import { deleteFile, downloadFile, uploadFile } from "../Services/file";

const HomePage = () => {
  const [startDate, setStartDate] = useState<Dayjs | null>(null);
  const [endDate, setEndDate] = useState<Dayjs | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [predictions, setPredictions] = useState<PredictResponse>([]);

  const { data: checkFileData, refetch: refetchCheckFile } = useCheckFile();

  const handlePredictClick = async () => {
    if (!startDate || !endDate) return;
    setLoading(true);
    try {
      const formattedStartDate = format(startDate.toDate(), "dd.MM.yyyy");
      const formattedEndDate = format(endDate.toDate(), "dd.MM.yyyy");
      const response: PredictResponse = await getPredictions(
        formattedStartDate,
        formattedEndDate
      );
      setPredictions(response);
    } catch (error) {
      enqueueSnackbar("Error getting predictions! Please try again", {
        variant: "error",
      });
      setLoading(false);
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async () => {
    try {
      await deleteFile();
      refetchCheckFile();
      enqueueSnackbar("File successfully deleted", { variant: "success" });
    } catch (error) {
      enqueueSnackbar("Failed to delete file", { variant: "error" });
    }
  };

  const handleUploadFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await uploadFile(formData);
      enqueueSnackbar("File successfully uploaded", { variant: "success" });
      refetchCheckFile();
    } catch (error) {
      enqueueSnackbar("Error uploading file", { variant: "error" });
    }
  };

  const handleDownloadFile = async (fileName: string) => {
    try {
      const fileData = await downloadFile();
      const url = window.URL.createObjectURL(new Blob([fileData]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      enqueueSnackbar("Error downloading file", { variant: "error" });
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
        style={{ minHeight: "100vh" }}
        spacing={5}
      >
        <Typography variant="h4" ml={3}>
          Lumen App Frontend
        </Typography>
        <Grid item>
          {checkFileData?.exists ? (
            <Grid
              container
              direction="row"
              alignItems="center"
              justifyContent="center"
              spacing={4}
            >
              <Grid item>
                <Typography>{checkFileData.filename}</Typography>
              </Grid>
              <Grid item>
                <Grid
                  container
                  direction="row"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Grid item>
                    <Tooltip title="Download .parquet file">
                      <IconButton
                        aria-label="download"
                        onClick={() =>
                          handleDownloadFile(checkFileData.filename ?? "")
                        }
                      >
                        <CloudDownloadIcon sx={{ color: "blue" }} />
                      </IconButton>
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <Tooltip title="Delete .parquet file">
                      <IconButton
                        aria-label="delete"
                        onClick={handleDeleteFile}
                      >
                        <DeleteIcon sx={{ color: "red" }} />
                      </IconButton>
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <Tooltip title="Valid .parquet file has been found on the server">
                      <IconButton sx={{ cursor: "default" }}>
                        <CheckCircleIcon sx={{ color: "green" }} />
                      </IconButton>
                    </Tooltip>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          ) : (
            <Button variant="contained" component="label">
              Upload .parquet File
              <input
                type="file"
                hidden
                onChange={handleUploadFile}
                accept=".parquet"
              />
            </Button>
          )}
        </Grid>
        <Grid item>
          <DatePicker
            value={startDate}
            onChange={(newValue) => setStartDate(newValue)}
          />
        </Grid>
        <Grid item>
          <DatePicker
            value={endDate}
            onChange={(newValue) => setEndDate(newValue)}
          />
        </Grid>
        <Grid item>
          <Button
            variant="contained"
            onClick={handlePredictClick}
            disabled={
              !startDate || !endDate || loading || !checkFileData?.exists
            }
          >
            Predict
          </Button>
        </Grid>
        {loading && (
          <Grid item>
            <CircularProgress />
          </Grid>
        )}
        {!loading && predictions && (
          <Grid item>
            {predictions.map((prediction, index) => (
              <div key={`prediction-${index}`}>
                <TextField disabled value={prediction.date} />
                {prediction.predictions.map((pred, index2) => (
                  <TextField
                    key={`prediction-${index}-${index2}`}
                    value={`Room id ${pred.room_id} : ${pred.room_cnt}`}
                  />
                ))}
              </div>
            ))}
          </Grid>
        )}
      </Grid>
    </LocalizationProvider>
  );
};

export default HomePage;
