package com.autopad.connection

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.autopad.protocol.AutopadMessage
import okhttp3.*
import java.util.concurrent.TimeUnit

class ConnectionManager(application: Application) : AndroidViewModel(application) {

    enum class ConnectionType { WIFI, BLUETOOTH, USB }
    enum class ConnectionState { DISCONNECTED, CONNECTING, CONNECTED }

    private val _connectionState = MutableLiveData(ConnectionState.DISCONNECTED)
    val connectionState: LiveData<ConnectionState> = _connectionState

    private val _connectionType = MutableLiveData(ConnectionType.WIFI)
    val connectionType: LiveData<ConnectionType> = _connectionType

    private val _lastMessage = MutableLiveData<AutopadMessage?>()
    val lastMessage: LiveData<AutopadMessage?> = _lastMessage

    private var webSocket: WebSocket? = null
    private var messageCallback: ((AutopadMessage) -> Unit)? = null

    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()

    fun setMessageCallback(callback: (AutopadMessage) -> Unit) {
        messageCallback = callback
    }

    fun connectWifi(ipAddress: String, port: Int = 8765) {
        _connectionState.postValue(ConnectionState.CONNECTING)
        _connectionType.postValue(ConnectionType.WIFI)

        val request = Request.Builder()
            .url("ws://$ipAddress:$port")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _connectionState.postValue(ConnectionState.CONNECTED)
                val connectMsg = AutopadMessage.connect("autopad-secure-token")
                webSocket.send(connectMsg.toJson())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                AutopadMessage.fromJson(text)?.let { msg ->
                    _lastMessage.postValue(msg)
                    messageCallback?.invoke(msg)
                }
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
                _connectionState.postValue(ConnectionState.DISCONNECTED)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.postValue(ConnectionState.DISCONNECTED)
            }
        })
    }

    fun connectBluetooth() {
        _connectionType.postValue(ConnectionType.BLUETOOTH)
        _connectionState.postValue(ConnectionState.DISCONNECTED)
    }

    fun connectUsb() {
        _connectionType.postValue(ConnectionType.USB)
        _connectionState.postValue(ConnectionState.CONNECTING)
        connectWifi("127.0.0.1", 8765)
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnect")
        webSocket = null
        _connectionState.postValue(ConnectionState.DISCONNECTED)
    }

    fun sendMessage(message: AutopadMessage) {
        webSocket?.send(message.toJson())
    }

    fun isConnected(): Boolean = _connectionState.value == ConnectionState.CONNECTED

    override fun onCleared() {
        super.onCleared()
        disconnect()
    }
}
