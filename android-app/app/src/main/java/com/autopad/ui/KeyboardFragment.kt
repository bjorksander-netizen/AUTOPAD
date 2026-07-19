package com.autopad.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.R
import com.autopad.connection.ConnectionManager
import com.autopad.protocol.AutopadMessage

class KeyboardFragment : Fragment() {

    private lateinit var connectionManager: ConnectionManager
    private val activeModifiers = mutableSetOf<String>()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_keyboard, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        connectionManager = ViewModelProvider(requireActivity())[ConnectionManager::class.java]

        val etInput = view.findViewById<EditText>(R.id.et_keyboard_input)

        etInput.setOnEditorActionListener { _, _, _ ->
            val text = etInput.text.toString()
            if (text.isNotEmpty() && connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.keyText(text))
                etInput.text.clear()
            }
            true
        }

        val keyMap = mapOf(
            R.id.key_q to "q", R.id.key_w to "w", R.id.key_e to "e",
            R.id.key_r to "r", R.id.key_t to "t", R.id.key_y to "y",
            R.id.key_u to "u",
            R.id.key_a to "a", R.id.key_s to "s", R.id.key_d to "d",
            R.id.key_f to "f", R.id.key_g to "g", R.id.key_h to "h",
            R.id.key_j to "j",
            R.id.key_z to "z", R.id.key_x to "x", R.id.key_c to "c",
            R.id.key_v to "v", R.id.key_b to "b", R.id.key_n to "n",
            R.id.key_m to "m"
        )

        keyMap.forEach { (id, key) ->
            view.findViewById<Button>(id)?.setOnClickListener {
                sendKeyPress(key)
            }
        }

        val modifierKeys = mapOf(
            R.id.key_ctrl to "ctrl",
            R.id.key_alt to "alt",
            R.id.key_shift to "shift",
            R.id.key_win to "win"
        )

        modifierKeys.forEach { (id, modifier) ->
            val btn = view.findViewById<Button>(id)
            btn?.setOnClickListener {
                if (activeModifiers.contains(modifier)) {
                    activeModifiers.remove(modifier)
                    btn.alpha = 0.6f
                } else {
                    activeModifiers.add(modifier)
                    btn.alpha = 1.0f
                }
            }
        }

        val functionKeys = mapOf(
            R.id.key_f1 to "f1", R.id.key_f2 to "f2", R.id.key_f3 to "f3",
            R.id.key_f4 to "f4", R.id.key_f5 to "f5", R.id.key_f6 to "f6",
            R.id.key_f7 to "f7", R.id.key_f8 to "f8", R.id.key_f9 to "f9",
            R.id.key_f10 to "f10", R.id.key_f11 to "f11", R.id.key_f12 to "f12"
        )

        functionKeys.forEach { (id, key) ->
            view.findViewById<Button>(id)?.setOnClickListener {
                sendKeyPress(key)
            }
        }

        view.findViewById<Button>(R.id.key_tab)?.setOnClickListener { sendKeyPress("tab") }
        view.findViewById<Button>(R.id.key_enter)?.setOnClickListener { sendKeyPress("enter") }
        view.findViewById<Button>(R.id.key_backspace)?.setOnClickListener { sendKeyPress("backspace") }
        view.findViewById<Button>(R.id.key_escape)?.setOnClickListener { sendKeyPress("escape") }
        view.findViewById<Button>(R.id.key_space)?.setOnClickListener { sendKeyPress("space") }
    }

    private fun sendKeyPress(key: String) {
        if (!connectionManager.isConnected()) return

        if (activeModifiers.isNotEmpty()) {
            val keys = mutableListOf<String>()
            keys.addAll(activeModifiers)
            keys.add(key)
            connectionManager.sendMessage(AutopadMessage.keyCombo(keys))
        } else {
            connectionManager.sendMessage(AutopadMessage.keyPress(key))
        }
    }
}
