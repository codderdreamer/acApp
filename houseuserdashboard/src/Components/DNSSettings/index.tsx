import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import React, { useEffect } from 'react';
import { useState } from "react";


interface Props {
  socket: W3CWebSocket | null;
  jsonString: string | null;
}

const DNSSettings : React.FC<Props> = ({ socket, jsonString }) => {
  const { t } = useTranslation();
  const [newSocket, setSocket] = useState(socket);
  const [newjsonString, setDNSSettings] = useState(jsonString);
  const [dnsEnable, setdnsEnable] = useState<boolean>(false);
  const [DNS1, setDNS1] = useState("");
  const [DNS2, setDNS2] = useState("");

  useEffect(() => {
    setDNSSettings(jsonString)
    if (jsonString) {
      const jsonData = JSON.parse(jsonString);
      setdnsEnable(jsonData.Data["dnsEnable"])
      setDNS1(jsonData.Data["DNS1"])
      setDNS2(jsonData.Data["DNS2"])
    }

  }, [jsonString]);

  async function SaveDNSSettings() {
    if (socket) {
      if (socket.readyState == socket.OPEN) {
        socket.send(JSON.stringify(
          {
            "Command" : "DNSSettings",
            "Data" : {
                        "dnsEnable" : dnsEnable,
                        "DNS1" : DNS1,
                        "DNS2" : DNS2
                    }
        }
        ))
      }
    }
  }

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("dns-configuration")}</h5>
            <div className="row">
              <div className="col-12">
                <input
                  type="checkbox"
                  name="dns_enabled"
                  checked={dnsEnable}
                  onChange={(e) => setdnsEnable(e.target.checked)}
                />
                <label htmlFor="dns-configuration">{t("dns-enable")}</label>
                <div
                  id="dns-configuration-form"
                >
                  <div className="row mb-3">
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("dns")} 1</label>
                      <input
                        name="wifi_dns1"
                        value={DNS1}
                        onChange={(e) => setDNS1(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("dns")} 2</label>
                      <input
                        name="wifi_dns2"
                        value={DNS2}
                        onChange={(e) => setDNS2(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                  </div>
                </div>
                <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
                  <button
                    className="btn btn-primary btn-sm mb-0"
                    type="button"
                    name="button"
                    onClick={SaveDNSSettings}
                  >
                    {t("submit")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DNSSettings;
