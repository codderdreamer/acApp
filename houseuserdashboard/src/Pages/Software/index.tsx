import GetVersion from "../../Components/GetVersion";
import OCPPSettings from "../../Components/OCPPSettings";
import FourGSettings from "../../Components/FourGSettings";
import NetworkPriority from "../../Components/NetworkPriority";
import EthernetSettings from "../../Components/EthernetSettings";
import WifiSettings from "../../Components/WifiSettings";
import DNSSettings from "../../Components/DNSSettings";
import FunctionsSettings from "../../Components/FunctionsSettings";
import BluetoothSettings from "../../Components/BluetoothSettings";
import TimeZoneSettings from "../../Components/TimeZoneSettings";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import { useState } from "react";
import React, { useEffect } from 'react';




const Software = () => {
  const { t } = useTranslation();
  const [socket, setSocket] = useState<W3CWebSocket | null>(null);
  const [networkjsonString, setNetworkPriority] = useState<string | null>(null);
  const [fourGSettingsString, setfourGSettingsString] = useState<string | null>(null);
  const [ethernetSettingsString, setethernetSettingsString] = useState<string | null>(null);
  const [DNSSettingsString, setDNSSettingsString] = useState<string | null>(null);
  const [WifiSettingsString, setWifiSettingsString] = useState<string | null>(null);

  useEffect(() => {
    const newSocket = new W3CWebSocket('ws://192.168.1.170:8000');

    newSocket.onopen = () => {
      console.log('WebSocket bağlantısı kuruldu.');
    };

    newSocket.onmessage = (message) => {
      const jsonData = JSON.parse(message.data.toString());
      console.log(jsonData)
      switch (jsonData.Command) {
        case "NetworkPriority":
          setNetworkPriority(message.data.toString());
          break
        case "4GSettings":
          setfourGSettingsString(message.data.toString());
          break
        case "EthernetSettings":
          setethernetSettingsString(message.data.toString());
          break
        case "DNSSettings":
          setDNSSettingsString(message.data.toString());
          break;
        case "WifiSettings":
          setWifiSettingsString(message.data.toString());
          break;

      }

    };

    newSocket.onerror = (error) => {
      console.error('WebSocket hatası:', error);
    };

    newSocket.onclose = () => {
      console.log('WebSocket bağlantısı kapatıldı.');
    };

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

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
                <img src="../assets/img/software_settings.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("software-settings")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        {/* network settings */}
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <h5 className="font-weight-bolder mb-4">
                  {t("network-settings")}
                </h5>
                <div className="row g-3">
                  <div className="col-12 col-md-6">
                    <NetworkPriority socket={socket} jsonString={networkjsonString} />
                  </div>
                  <div className="col-12 col-md-6">
                    <FourGSettings socket={socket} jsonString={fourGSettingsString} />
                  </div>
                  <div className="col-12 col-md-6">
                    <EthernetSettings socket={socket} jsonString={ethernetSettingsString} />
                  </div>
                  <div className="col-12 col-md-6">
                    <DNSSettings socket={socket} jsonString={DNSSettingsString} />
                  </div>
                  <div className="col-12 col-md-6">
                    {/* <WifiSettings socket={socket} jsonString={WifiSettingsString} /> */}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* ocpp settings */}
        <OCPPSettings />
        {/* functions config */}
        <FunctionsSettings />
        {/* utc time settings */}
        <TimeZoneSettings />
        {/* bluetooth */}
        <BluetoothSettings />
        {/* get version */}
        <GetVersion />
      </div>
    </>
  );
};

export default Software;
