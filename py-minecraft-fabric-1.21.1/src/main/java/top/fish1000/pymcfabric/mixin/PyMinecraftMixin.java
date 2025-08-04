package top.fish1000.pymcfabric.mixin;

import net.minecraft.server.MinecraftServer;
import net.minecraft.util.profiler.Profiler;
import top.fish1000.pymcfabric.utils;
import top.fish1000.pymcfabric.executor.SimpleExecutor;

import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(MinecraftServer.class)
public abstract class PyMinecraftMixin {

    @Shadow
    public Profiler profiler;

    @Shadow
    public int ticks;

    public final SimpleExecutor<MinecraftServer> executor = new SimpleExecutor<>(() -> ticks);

    @Inject(at = @At(value = "INVOKE", target = "Lnet/minecraft/server/function/CommandFunctionManager;tick()V", shift = At.Shift.AFTER), method = "tickWorlds()V")
    private void tick(CallbackInfo info) {
        profiler.swap("py4j");
        // long start = System.nanoTime();
        executor.tick((MinecraftServer) (Object) this);
        // long end = System.nanoTime();
        // utils.LOGGER.info("py4j tick: {}ms", (end - start) / 1000000d);
    }
}
