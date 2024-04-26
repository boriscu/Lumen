import { useQuery } from "react-query";
import { checkFile } from "../Services/file";

export const useCheckFile = () => {
  return useQuery(["checkFileKey"], () => checkFile(), {
    keepPreviousData: true,
    refetchInterval: 5000,
  });
};
