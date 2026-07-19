package com.autopad.ui

import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import android.app.AlertDialog
import android.widget.LinearLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.R
import com.autopad.MainActivity
import com.autopad.connection.ConnectionManager

class HomeFragment : Fragment() {

    private lateinit var connectionManager: ConnectionManager

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_home, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        connectionManager = ViewModelProvider(requireActivity())[ConnectionManager::class.java]

        val tvStatus = view.findViewById<TextView>(R.id.tv_status)
        val tvConnectionInfo = view.findViewById<TextView>(R.id.tv_connection_info)
        val statusIndicator = view.findViewById<View>(R.id.status_indicator)
        val btnConnect = view.findViewById<Button>(R.id.btn_connect)
        val cardTrackpad = view.findViewById<View>(R.id.card_trackpad)
        val cardKeyboard = view.findViewById<View>(R.id.card_keyboard)
        val cardMedia = view.findViewById<View>(R.id.card_media)
        val cardClipboard = view.findViewById<View>(R.id.card_clipboard)

        connectionManager.connectionState.observe(viewLifecycleOwner) { state ->
            when (state) {
                ConnectionManager.ConnectionState.CONNECTED -> {
                    tvStatus.text = getString(R.string.connected)
                    tvConnectionInfo.text = "Tap feature cards below to start"
                    val indicator = statusIndicator.background as? GradientDrawable
                    indicator?.setColor(resources.getColor(R.color.success_green, null))
                    btnConnect.text = getString(R.string.disconnect)
                }
                ConnectionManager.ConnectionState.CONNECTING -> {
                    tvStatus.text = getString(R.string.connecting)
                    tvConnectionInfo.text = "Please wait..."
                    val indicator = statusIndicator.background as? GradientDrawable
                    indicator?.setColor(resources.getColor(R.color.warning_yellow, null))
                }
                ConnectionManager.ConnectionState.DISCONNECTED -> {
                    tvStatus.text = getString(R.string.disconnected)
                    tvConnectionInfo.text = "Tap to connect"
                    val indicator = statusIndicator.background as? GradientDrawable
                    indicator?.setColor(resources.getColor(R.color.error_red, null))
                    btnConnect.text = getString(R.string.connect_to_desktop)
                }
            }
        }

        btnConnect.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.disconnect()
            } else {
                showConnectDialog()
            }
        }

        cardTrackpad.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_trackpad)
        }
        cardKeyboard.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_keyboard)
        }
        cardMedia.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_keyboard)
        }
        cardClipboard.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_clipboard)
        }
    }

    private fun showConnectDialog() {
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_connect, null)
        val etIpAddress = dialogView.findViewById<EditText>(R.id.et_ip_address)
        val btnConnectWifi = dialogView.findViewById<Button>(R.id.btn_connect_wifi)
        val btnConnectBluetooth = dialogView.findViewById<Button>(R.id.btn_connect_bluetooth)
        val btnConnectUsb = dialogView.findViewById<Button>(R.id.btn_connect_usb)

        val dialog = AlertDialog.Builder(context)
            .setView(dialogView)
            .setCancelable(true)
            .create()

        dialog.window?.setBackgroundDrawableResource(R.color.secondary_bg)

        btnConnectWifi.setOnClickListener {
            val ip = etIpAddress.text.toString().trim()
            if (ip.isNotEmpty()) {
                connectionManager.connectWifi(ip)
                dialog.dismiss()
            } else {
                Toast.makeText(context, "Enter IP address", Toast.LENGTH_SHORT).show()
            }
        }

        btnConnectBluetooth.setOnClickListener {
            connectionManager.connectBluetooth()
            Toast.makeText(context, "Bluetooth: Coming soon", Toast.LENGTH_SHORT).show()
        }

        btnConnectUsb.setOnClickListener {
            connectionManager.connectUsb()
            dialog.dismiss()
        }

        dialog.show()
    }
}
