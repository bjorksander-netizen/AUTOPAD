package com.autopad.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.R
import com.autopad.connection.ConnectionManager
import com.autopad.protocol.AutopadMessage
import com.google.android.material.slider.Slider

class MediaFragment : Fragment() {

    private lateinit var connectionManager: ConnectionManager

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_media, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        connectionManager = ViewModelProvider(requireActivity())[ConnectionManager::class.java]

        val btnPlayPause = view.findViewById<Button>(R.id.btn_play_pause)
        val btnPrevious = view.findViewById<Button>(R.id.btn_previous)
        val btnNext = view.findViewById<Button>(R.id.btn_next)
        val sliderVolume = view.findViewById<Slider>(R.id.slider_volume)
        val tvVolume = view.findViewById<TextView>(R.id.tv_volume)
        val btnMute = view.findViewById<Button>(R.id.btn_mute)

        btnPlayPause.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mediaPlayPause())
            }
        }

        btnPrevious.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mediaPrevious())
            }
        }

        btnNext.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mediaNext())
            }
        }

        sliderVolume.addOnChangeListener { _, value, fromUser ->
            if (fromUser) {
                tvVolume.text = "${value.toInt()}%"
                if (connectionManager.isConnected()) {
                    connectionManager.sendMessage(AutopadMessage.volumeSet(value.toInt()))
                }
            }
        }

        btnMute.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.volumeMute())
            }
        }
    }
}
