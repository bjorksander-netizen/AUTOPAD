package com.autopad.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.R
import com.autopad.connection.ConnectionManager
import com.autopad.protocol.AutopadMessage
import com.google.android.material.switchmaterial.SwitchMaterial

class ClipboardFragment : Fragment() {

    private lateinit var connectionManager: ConnectionManager
    private var autoSyncEnabled = true
    private var desktopClipboard = ""
    private var phoneClipboard = ""
    private val handler = Handler(Looper.getMainLooper())

    private val clipboardListener = ClipboardManager.OnPrimaryClipChangedListener {
        val clipboardManager = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboardManager.primaryClip
        if (clip != null && clip.itemCount > 0) {
            val text = clip.getItemAt(0).text?.toString() ?: ""
            if (text.isNotEmpty() && text != phoneClipboard) {
                phoneClipboard = text
                updatePhoneClipboardView()
                if (autoSyncEnabled && connectionManager.isConnected()) {
                    connectionManager.sendMessage(AutopadMessage.clipboardChanged(text, "android"))
                }
            }
        }
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_clipboard, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        connectionManager = ViewModelProvider(requireActivity())[ConnectionManager::class.java]

        val switchAutoSync = view.findViewById<SwitchMaterial>(R.id.switch_auto_sync)
        val tvDesktopClipboard = view.findViewById<TextView>(R.id.tv_desktop_clipboard)
        val tvPhoneClipboard = view.findViewById<TextView>(R.id.tv_phone_clipboard)
        val btnCopyToPhone = view.findViewById<Button>(R.id.btn_copy_to_phone)
        val btnCopyToDesktop = view.findViewById<Button>(R.id.btn_copy_to_desktop)
        val tvStatus = view.findViewById<TextView>(R.id.tv_clipboard_status)

        switchAutoSync.setOnCheckedChangeListener { _, isChecked ->
            autoSyncEnabled = isChecked
        }

        btnCopyToPhone.setOnClickListener {
            if (desktopClipboard.isNotEmpty()) {
                val clipboardManager = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clip = ClipData.newPlainText("AUTOPAD", desktopClipboard)
                clipboardManager.setPrimaryClip(clip)
                Toast.makeText(context, "Copied to phone clipboard", Toast.LENGTH_SHORT).show()
            }
        }

        btnCopyToDesktop.setOnClickListener {
            if (phoneClipboard.isNotEmpty() && connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.clipboardSync(phoneClipboard, "android"))
                Toast.makeText(context, "Sent to desktop", Toast.LENGTH_SHORT).show()
            }
        }

        connectionManager.lastMessage.observe(viewLifecycleOwner) { message ->
            message?.let {
                when (it.type) {
                    "CLIPBOARD_CHANGED", "CLIPBOARD_SYNC" -> {
                        val content = it.data["content"]?.toString() ?: ""
                        val source = it.data["source"]?.toString() ?: ""
                        if (source == "windows") {
                            desktopClipboard = content
                            tvDesktopClipboard.text = content.ifEmpty { getString(R.string.clipboard_empty) }
                            tvStatus.text = "Last synced: just now"
                        }
                    }
                }
            }
        }

        val clipboardManager = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboardManager.addPrimaryClipChangedListener(clipboardListener)

        if (connectionManager.isConnected()) {
            connectionManager.sendMessage(AutopadMessage.clipboardPull())
        }
    }

    private fun updatePhoneClipboardView() {
        view?.findViewById<TextView>(R.id.tv_phone_clipboard)?.text =
            phoneClipboard.ifEmpty { getString(R.string.clipboard_empty) }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        val clipboardManager = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboardManager.removePrimaryClipChangedListener(clipboardListener)
    }
}
