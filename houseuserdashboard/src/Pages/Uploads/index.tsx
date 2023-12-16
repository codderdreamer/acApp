import { useState } from "react";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { utils as XLSXUtils, writeFile as XLSXWriteFile } from "xlsx";

const Uploads = () => {
  const [File, setFile] = useState<any>(null);
  const [StartDate, setStartDate] = useState<string>("");
  const [EndDate, setEndDate] = useState<string>("");
  const [Loading, setLoading] = useState<boolean>(false);

  const { t } = useTranslation();

  async function UploadUpdate() {
    // const result = await UploadDS(File, "update");
    // if (result.data.status) {
    //   toast.success(t("upload-successful"));
    // } else {
    //   toast.error(t("upload-failed"));
    // }
  }

  async function GetLogs() {
    // if (!StartDate || !EndDate) return toast.error(t("select-date"));
    // setLoading(true);
    // let startDate = new Date(StartDate).toISOString().split("T")[0];
    // let endDate = new Date(EndDate).toISOString().split("T")[0];
    // const logs = (await GetLogsWithDateRangeDS(startDate, endDate)).data;
    // const logsSheet = XLSXUtils.json_to_sheet(logs.logs);
    // const errorsSheet = XLSXUtils.json_to_sheet(logs.errors);
    // const workbook = XLSXUtils.book_new();
    // XLSXUtils.book_append_sheet(workbook, logsSheet, "Logs");
    // XLSXUtils.book_append_sheet(workbook, errorsSheet, "Errors");
    // XLSXWriteFile(workbook, "logs.xlsx");
    // setLoading(false);
  }

  return (
    <>
      <div
        className="card shadow-lg mx-4 card-profile-bottom"
        style={{ marginTop: "12rem" }}
      >
        <div className="card-body p-3">
          <div className="row gx-4">
            <div className="col-auto">
              <div className="avatar avatar-xl position-relative">
                <img src="../assets/img/upload_download.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("upload-and-download")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        {/* upload update */}
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <div className="row mb-3">
                  <div className="col-12">
                    <label>{t("ubi-firmware-upload")}</label>
                    <input
                      id="ubifile"
                      className="form-control"
                      type="file"
                      accept=".gz"
                      onChange={(e) => {
                        if (e.target && e.target.files) {
                          setFile(e.target.files[0]);
                        }
                      }}
                    />
                  </div>
                </div>
                <button
                  disabled={!File}
                  id="addbtn"
                  className="btn btn-primary btn-sm mb-0"
                  type="button"
                  name="button"
                  onClick={UploadUpdate}
                >
                  {t("submit")}
                </button>
              </div>
            </div>
          </div>
        </div>
        {/* log download */}
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <h5 className="font-weight-bolder">{t("log-download")}</h5>
                <div className="row mb-3">
                  <div className="col-6">
                    <label>{t("start-date")}</label>
                    <input
                      className="form-control"
                      type="date"
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div className="col-6">
                    <label>{t("end-date")}</label>
                    <input
                      className="form-control"
                      type="date"
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <button
                  disabled={Loading}
                  className="btn btn-primary btn-sm mb-0"
                  type="button"
                  name="button"
                  onClick={GetLogs}
                >
                  {t("submit")}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Uploads;
