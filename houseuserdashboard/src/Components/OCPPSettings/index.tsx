import { toast } from "react-toastify";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import React, { useEffect } from 'react';

interface Props {
  socket: W3CWebSocket | null;
  jsonString: string | null;
}

const OCPPSettings = () => {
  const [File, setFile] = useState<any>(null);
  const { t } = useTranslation();

  async function UploadCert() {
    // const result = await UploadDS(File, "cert");
    // if (result.data.status) {
    //   toast.success(t("upload-successful"));
    // } else {
    //   toast.error(t("upload-successful"));
    // }
  }

  async function SaveOCPPSettings() {
    // await SetDS({ key: 'ip', value: Values.data.ip })
    // await SetDS({ key: 'ocpp_port', value: Values.data.ocpp_port })
    // await SetDS({ key: 'ssl_enable', value: Values.data.ssl_enable })
    // await SetDS({ key: 'path1', value: Values.data.path1 })
    // await SetDS({ key: 'authorization_key', value: Values.data.authorization_key })
    // toast.success(t('save-successful'))
  }

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("ocpp-settings")}</h5>
            <div className="row">
              <div className="col-12 col-sm-6">
                <label>{t("ip-or-domain-name")}</label>
                <input
                  name="ip"
                  // value={Values.data.ip}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                  type="text"
                />
              </div>
              <div className="col-12 col-sm-6 mt-3 mt-sm-0">
                <label>{t("Port")}</label>
                <input
                  name="ocpp_port"
                  // value={Values.data.ocpp_port}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                  type="text"
                />
              </div>
            </div>
            <div className="row">
              <div className="col-6">
                <label className="mt-4">{t("ssl-enable")}</label>
                <select
                  name="ssl_enable"
                  // value={Values.data.ssl_enable}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value={1}>{t("enable")}</option>
                  <option value={0}>{t("disable")}</option>
                </select>
              </div>
              <div className="col-6">
                <label className="mt-4">{t("path")}</label>
                <input
                  name="path1"
                  // value={Values.data.path1}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                  type="text"
                />
              </div>
            </div>
            <div className="row mb-3">
              <div className="col-12">
                <label className="mt-4">{t("authorization-key")}</label>
                <input
                  name="authorization_key"
                  // value={Values.data.authorization_key}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                  type="text"
                />
              </div>
            </div>
            <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
              <button
                className="btn btn-primary btn-sm"
                type="button"
                name="button"
                onClick={SaveOCPPSettings}
              >
                {t("submit")}
              </button>
            </div>
            <div className="row mb-3">
              <div className="col-12">
                <label className="mt-4">{t("certificate-import")}</label>
                <input
                  id="certfile"
                  className="form-control"
                  type="file"
                  accept=".ca"
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
              className="btn btn-primary btn-sm"
              type="button"
              name="button"
              onClick={UploadCert}
            >
              {t("submit")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OCPPSettings;
